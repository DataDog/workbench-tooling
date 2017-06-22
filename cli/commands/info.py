import click
from cli.cli import pass_context


@click.command('info')
@pass_context
def cli(ctx):
    click.echo('This is a cli !')

