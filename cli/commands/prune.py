import click
from cli.cli import pass_context
from cli import state


@click.command('prune', short_help='Prune docker')
@pass_context
def cli(ctx):
    ctx.sh("docker system prune")
