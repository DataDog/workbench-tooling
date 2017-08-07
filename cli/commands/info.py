import click

from cli.cli import pass_context


@click.command('info', short_help='Show the current state of the workbench')
@pass_context
def cli(ctx):
    """
    Show the current state of the workbench.
    """
    click.echo("========")
    click.echo("Settings")
    click.echo("========\n")
    ctx.setting.display()

    click.echo("\n=====")
    click.echo("State")
    click.echo("=====\n")
    ctx.state.display()

    click.echo("\n========")
    click.echo("Dev Mode")
    click.echo("========\n")
    ctx.dev_mode.display()

    click.echo("\n=======")
    click.echo("Recipes")
    click.echo("=======\n")
    ctx.recipes.display()
