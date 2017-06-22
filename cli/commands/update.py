import os

import click
import git

from cli.cli import pass_context


@click.command('update', short_help='Update/Initializes the local clone of workbench-recipes')
@pass_context
def cli(ctx):
    """
    Update/Initializes the local clone of workbench-recipes.

    This will clone or pull the local clone of workbench-recipes and refresh caches
    """
    target_dir = os.path.join(ctx.local_data, "workbench-recipes")

    if not os.path.exists(os.path.join(target_dir, ".git")):
        click.echo('cloning workbench-recipes to %s' % target_dir)
        os.makedirs(target_dir)
        git.Repo.clone_from("https://github.com/DataDog/workbench-recipes.git", target_dir)
    else:
        click.echo('pulling latest changes from workbench-recipes')
        click.echo(git.cmd.Git(target_dir).pull())
