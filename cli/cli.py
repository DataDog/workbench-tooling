import os
import sys
import subprocess
import errno
import click
import helper

CONTEXT_SETTINGS = dict(auto_envvar_prefix='WORKBENCH')


class Context(object):
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()
        self.recipes_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "DataDog", "workbench-recipes")
        self.local_config = os.path.join(os.path.expanduser("~"), ".config", "DataDog", "workbench")
        self.conf_d_dir = os.path.join(self.local_config, "conf.d")
        self.auto_conf_dir = os.path.join(self.conf_d_dir, "auto_conf")

        for path in (self.auto_conf_dir, self.recipes_dir):
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                pass

        # cache loading
        self.cache_file = os.path.join(self.local_config, "recipes_cache.json")
        self.setting_file = os.path.join(self.local_config, "setting.json")
        self.state_file = os.path.join(self.local_config, "state.json")

        # for now we initialize every internal file here
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "w") as f:
                f.write("{}")

        if not os.path.exists(self.state_file):
            with open(self.state_file, "w") as f:
                f.write('{"running": {}}')

        if not os.path.exists(self.setting_file):
            with open(self.setting_file, "w") as f:
                f.write('{}')

        self.recipes_cache = helper.load_cache(self)

    def vlog(self, msg):
        if self.verbose:
            click.echo(msg)

    def fail(self, msg):
        click.echo(msg, file=sys.stderr)
        sys.exit(1)

    def sh(self, cmd):
        self.vlog(cmd)
        subprocess.check_call(cmd, shell=True)


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and filename != "__init__.py":
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('cli.commands.' + name, None, None, ['cli'])
        except ImportError as e:
            print "Error loading %s: %s" % (name, e)
            raise
        return mod.cli


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))


@click.command(cls=ComplexCLI)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@pass_context
def cli(ctx, verbose):
    """ main CLI for workbench """
    ctx.verbose = verbose
