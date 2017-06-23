import os

import click
import git
import yaml

from cli.cli import pass_context

def check_not_void(value):
    return((isinstance(value, dict) or isinstance(value, list) ) and len(value) > 0)

def check_auto_conf(file_name, conf):
    checks_ok = True
    if "docker_images" not in conf:
        click.echo("auto_conf file %s ill formatted: docker_images section has to exist" % file_name)
        checks_ok = False
    else:
        if not(check_not_void(conf["docker_images"])):
            click.echo("auto_conf file %s ill formatted: docker_images section should not be empty" % file_name)
            checks_ok = False
    if "init_config" not in conf:
        click.echo("auto_conf file %s ill formatted: init_config section has to exist" % file_name)
        checks_ok = False
    if "instances" not in conf:
        click.echo("auto_conf file %s ill formatted: instances section has to exist" % file_name)
        checks_ok = False
    else:
        if not(check_not_void(conf["instances"])):
            click.echo("auto_conf file %s ill formatted: instances section should not be empty" % file_name)
            checks_ok = False
    return(checks_ok)

def check_manifest(file_name, conf):
    checks_ok = True
    if "name" not in conf:
        click.echo("manifest.yaml %s ill formatted: name entry has to exist" % file_name)
        checks_ok = False
    if "flavors" not in conf:
        click.echo("manifest.yaml %s ill formatted: flavors section has to exist" % file_name)
        checks_ok = False
    else:
        if not(check_not_void(conf["flavors"])):
            click.echo("auto_conf file %s ill formatted: flavors section should not be empty" % file_name)
            checks_ok = False
    return(checks_ok)

@click.command('lint', short_help='Check the syntax of workbench-recipes YAMLs')

@pass_context
def cli(ctx):
    """
    Check yaml syntax in files imported from recipes repository 
    """
    path = ctx.recipes_dir
    checks_ok = True
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".yaml"):
                    with open(os.path.join(root, name)) as stream:
                        try:
                            integration_yaml = yaml.load(stream)
                            # check if correct auto_conf/int.py or manifest.py file
                            if root.endswith(("auto_conf", "auto_conf/")):
                                checks_ok = checks_ok and check_auto_conf(os.path.join(root, name), integration_yaml)
                            elif name == "manifest.yaml":
                                checks_ok = checks_ok and check_manifest(os.path.join(root, name), integration_yaml)
                            else:
                                ctx.vlog("Skipping checks for unknown file %s" % name)
                        except yaml.YAMLError as e:
                            click.echo('Syntax error in YAML file: {0}'.format(e))
                            checks_ok = False
                        except Exception as e:
                            click.echo('Error while parsing the YAML: {0}'.format(e))
    except os.error as err:
        click.echo("ERROR while reading yamls: {0}:".format(err))

    if checks_ok:
        click.echo("YAML files in workbench-recipes are formatted correctly!")
