import os

import click
import git

from cli.cli import pass_context
from cli import helper
from cli.helper import State


@click.command('update', short_help='Update/Initializes the local clone of workbench-recipes')
@pass_context
def cli(ctx):
    """
    Update/Initializes the local clone of workbench-recipes.

    This will clone or pull the local clone of workbench-recipes and refresh caches
    """
    state = State.get_state(ctx)
    if state and len(state['running']) > 0:
        ctx.fail("Some recipes are running, please stop then before running an update")

    if not os.path.exists(os.path.join(ctx.recipes_dir, ".git")):
        click.echo('cloning workbench-recipes to %s' % ctx.recipes_dir)
        git.Repo.clone_from("https://github.com/DataDog/workbench-recipes.git", ctx.recipes_dir)
    else:
        click.echo('pulling latest changes from workbench-recipes')
        click.echo(git.cmd.Git(ctx.recipes_dir).pull())

    # Regenerate cache
    helper.generate_cache(ctx)
    helper.update_auto_confs(ctx)
