import click
from cli.cli import pass_context


@click.command('info', short_help='info')
@pass_context
def cli(ctx):
    """Initializes a repository."""
    click.echo('This is a cli !')
