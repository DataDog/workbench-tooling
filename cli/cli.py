import os
import sys
import click


CONTEXT_SETTINGS = dict(auto_envvar_prefix='WORKBENCH')

class Context(object):

    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()
        self.local_data = os.path.join(os.path.expanduser("~"), ".local", "share", "DataDog")

pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))

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
            return
        except Excetion as e:
            print "Invalid import of %s: %s" % (name, e)
            return
        return mod.cli

@click.command(cls=ComplexCLI)
@click.option('-v', '--verbose', is_flag=True,
                      help='Enables verbose mode.')
@pass_context
def cli(ctx, verbose):
    """ main CLI for workbench """
    ctx.verbose = verbose
