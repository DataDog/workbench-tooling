import click

from cli.cli import pass_context
from cli import recipes


@click.command('update', short_help='Update/Initializes the local clone of workbench-recipes')
@pass_context
def cli(ctx):
    """
    Update/Initializes the local clone of workbench-recipes.

    This will clone or pull the local clone of workbench-recipes and refresh caches
    """
    recipes.update(ctx)
