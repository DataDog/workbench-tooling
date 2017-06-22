import click
import os
import sys


class Context(object):

    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()

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
            mod = __import__('commands.' + name, None, None, ['cli'])
        except ImportError as e:
            return
        return mod.cli

@click.command(cls=ComplexCLI)
@pass_context
def cli(ctx):
    pass

if __name__ == "__main__":
    cli()
