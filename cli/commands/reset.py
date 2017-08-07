import click
import shutil

from cli.cli import pass_context


@click.command('reset', short_help='Stop every recipes and clean every local file')
@pass_context
def cli(ctx):
    """
    Show the current state of the workbench.
    """
    click.echo("Stopping all recipes")
    ctx.state.stop_all()

    click.echo("Reseting dev_mode")
    ctx.dev_mode.deactivate_all_integration()

    click.echo("Removing local file")
    click.echo("- %s" % ctx.local_config)
    shutil.rmtree(ctx.local_config)
    click.echo("- %s" % ctx.local_data)
    shutil.rmtree(ctx.local_data)
