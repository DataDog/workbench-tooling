import os
from subprocess import CalledProcessError

import click
import yaml
from cerberus import Validator, DocumentError

from cli.cli import pass_context
from cli.recipes import MANIFEST_FILENAME, AUTOCONF_FOLDER_NAME

MANIFEST_SCHEMA = {
    'name': {'type': 'string', 'required': True, 'regex': '\S+'},
    'type': {'type': 'string', 'allowed': ['agent']},
    'flavors': {
        'type': 'dict',
        'required': True,
        'keyschema': {'type': 'string', 'regex': '\S+'},
        'valueschema': {
            'type': 'dict',
            'schema': {
                'description': {'type': 'string', 'required': True},
                'compose_file': {'type': 'string', 'valid_compose': True, 'required': True},
                'options': {
                    'type': 'dict',
                    'keyschema': {'type': 'string', 'regex': '\S+'},
                    'valueschema': {
                        'type': 'dict',
                        'schema': {
                            'description': {'type': 'string', 'required': True},
                            'values': {'type': 'list', 'schema': {'type': 'string'}},
                            'default': {'type': 'string'}
                        }
                    },
                },
                'settings': {
                    'type': 'dict',
                    'keyschema': {'type': 'string', 'regex': '\S+'},
                    'valueschema': {'type': 'string', 'allowed': ['required', 'optional']},
                }
            },
        }
    }
}

COMPOSE_SCHEMA = {
    'services': {
        'type': 'dict',
        'required': True,
        'valueschema': {
            'type': 'dict',
            'schema': {
                'build': {'required': False, 'find_dockerfile': True}
            }
        }
    },
    'networks': {'type': 'dict', 'required': True, 'has_workbench': True}
}

AUTOCONF_SCHEMA = {
    'docker_images': {'type': 'list', 'required': True, 'schema': {'type': 'string'}},
    'init_config': {'type': 'dict', 'required': True, 'nullable': True},
    'instances': {'type': 'list', 'required': True, 'nullable': True},
}


class YAMLValidator(Validator):
    """
    Wrapper class for cerberus.Validator that takes a file as input
    and reads YAML to validate from here, handling IO and parsing errors

    Constructors has an optional recursive argument. If true (default), validator
    may validate linked files if a rule is set in the schema
    """
    def __init__(self, *args, **kwargs):
        super(YAMLValidator, self).__init__(*args, **kwargs)
        self._config['recursive'] = kwargs.pop('recursive', True)
        self._config['quick'] = kwargs.pop('quick', False)
        self._config['ctx'] = kwargs.pop('ctx')

    def validate_file(self, folder, filename):
        try:
            self._config['path'] = folder
            with open(os.path.join(folder, filename)) as stream:
                contents = yaml.load(stream)
                return self.validate(contents)
        except DocumentError as e:
            self._error("Validation error", str(e))
            return False
        except IOError as e:
            self._error("File error", str(e))
            return False
        except yaml.YAMLError as e:
            self._error("YAML error", str(e))
            return False


class ManifestValidator(YAMLValidator):
    """
    Validates manifest.yaml files with an exhaustive schema.
    If recursive=True, validates linked docker compose files.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('schema', MANIFEST_SCHEMA)
        kwargs.setdefault('allow_unknown', False)
        super(ManifestValidator, self).__init__(*args, **kwargs)
        if self._config['recursive']:
            self._config['compose_validator'] = ComposeValidator(ctx=self._config['ctx'], quick=self._config['quick'])

    def _validate_valid_compose(self, do_validate, field, value):
        """
        Validates whether the docker compose file exists and,
        if recursive=True, validates its syntax with ComposeValidator

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not do_validate:
            return

        compose_path = "%s/%s" % (self._config['path'], value)
        if not os.path.isfile(compose_path):
            self._error(field, "specified file does not exist")
        elif self._config['recursive']:
            valid = self._config['compose_validator'].validate_file(self._config['path'], value)
            if not valid:
                self._error("%s syntax" % field, str(self._config['compose_validator'].errors))


class ComposeValidator(YAMLValidator):
    """
    Validates manifest.yaml files with a partial schema + `docker-compose config`
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('schema', COMPOSE_SCHEMA)
        kwargs.setdefault('allow_unknown', True)
        super(ComposeValidator, self).__init__(*args, **kwargs)

    def validate_file(self, folder, filename):
        try:
            if not self._config['quick']:
                cmd = "docker-compose -f %s/%s config -q" % (folder, filename)
                self._config['ctx'].sh(cmd)
        except CalledProcessError:
            raise DocumentError("docker-compose config failed for %s/%s" % (folder, filename))
        return super(ComposeValidator, self).validate_file(folder, filename)

    def _validate_has_workbench(self, do_validate, field, value):
        """
        {'type': 'boolean'}
        """
        if not do_validate:
            return

        default_net = value.get('default', {}).get('external', {}).get('name', None)
        if not default_net == "workbench":
            self._error(field, "must use the workbench network as default")

    def _validate_find_dockerfile(self, do_validate, field, value):
        """
        {'type': 'boolean'}
        """
        if not do_validate:
            return

        dockerfile_path = ""
        if isinstance(value, str):
            dockerfile_path = "%s/%s/Dockerfile" % (self._config['path'], value)
        elif isinstance(value, dict):
            dockerfile_path = "%s/%s/%s" % (self._config['path'],
                                            value.get("context", ""),
                                            value.get("dockerfile", "Dockerfile"))

        if not os.path.isfile(dockerfile_path):
            self._error(field, "Invalid dockerfile path: %s" % dockerfile_path)


class AutoConfValidator(YAMLValidator):
    """
    Validates autoconf files with a partial schema.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('schema', AUTOCONF_SCHEMA)
        kwargs.setdefault('allow_unknown', True)
        super(AutoConfValidator, self).__init__(*args, **kwargs)


@click.command('lint', short_help='Check the syntax of workbench-recipes YAMLs')
@click.argument('folders', nargs=-1)
@click.option('--quick', is_flag=True, help='Skip external linters')
@pass_context
def cli(ctx, folders, quick):
    """
    Check syntax in recipes in database, or custom folders if given
    """
    linted_ok = [0, 0]  # manifests, auto_conf
    linted_nok = [0, 0]

    manifest_validator = ManifestValidator(recursive=True, ctx=ctx, quick=quick)
    autoconf_validator = AutoConfValidator(ctx=ctx)

    folders = folders or [ctx.recipes_dir]
    for folder in folders:
        for path, _, files in os.walk(folder):
            for name in files:
                if name.endswith(MANIFEST_FILENAME):
                    if manifest_validator.validate_file(path, name):
                        ctx.vlog("%s/%s: OK" % (path, name))
                        linted_ok[0] += 1
                    else:
                        click.secho("%s/%s: NOK" % (path, name), fg='red')
                        click.echo(manifest_validator.errors)
                        click.echo(" ")
                        linted_nok[0] += 1

                if path.endswith(AUTOCONF_FOLDER_NAME) and name.endswith(".yaml"):
                    if autoconf_validator.validate_file(path, name):
                        ctx.vlog("%s/%s: OK" % (path, name))
                        linted_ok[1] += 1
                    else:
                        click.secho("%s/%s: NOK" % (path, name), fg='red')
                        click.echo(autoconf_validator.errors)
                        click.echo(" ")
                        linted_nok[1] += 1

    click.echo("")
    if sum(linted_nok) == 0:
        click.secho("All OK in %s manifests and %s auto_conf templates" % tuple(linted_ok), fg='green')
    else:
        click.echo("%s manifests and %s auto_conf templates are valid" % tuple(linted_ok))
        click.secho("%s manifests and %s auto_conf templates are invalid" % tuple(linted_nok), fg='red')
        raise click.Abort  # return error code for CI
