import click

from cli.cli import pass_context
from cli import state
from cli import setting
from cli import recipes


@click.command('info', short_help='Show the current state of the workbench')
@pass_context
def cli(ctx):
    """
    Show the current state of the workbench.
    """
    click.echo("========")
    click.echo("Settings")
    click.echo("========\n")
    setting.display(ctx)

    click.echo("\n=====")
    click.echo("State")
    click.echo("=====\n")
    state.display(ctx)

    click.echo("\n=======")
    click.echo("Recipes")
    click.echo("=======\n")
    recipes.display(ctx)
