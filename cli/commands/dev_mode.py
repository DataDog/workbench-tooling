import click
from cli.cli import pass_context


@click.group("dev_mode")
def cli():
    """Manages development mode."""

@cli.command("activate_integration", short_help="activate a local integration")
@click.argument('integration_name')
@pass_context
def activate_integration(ctx, integration_name):
    click.echo("Activating %s" % integration_name)
    try:
        ctx.dev_mode.activate_integration(integration_name)
    except Exception as e:
        ctx.fail(e)

@cli.command("deactivate_integration", short_help="deactivate a local integration")
@click.argument('integration_names', nargs=-1)
@click.option('-a', is_flag=True, help='deactivate all integrations.')
@pass_context
def deactivate_integration(ctx, integration_names, a):
    if a:
        ctx.dev_mode.deactivate_all_integration()
    else:
        ctx.dev_mode.deactivate_integration(integration_names)

@cli.command("ls", short_help="list activated integration")
@pass_context
def ls(ctx):
    ctx.dev_mode.list_integration()

@cli.command("set_repo_path", short_help="Set a local repository of integration (integrations-core or integrations-extras)")
@click.argument('repo_path')
@pass_context
def set_repo_path(ctx, repo_path):
    ctx.dev_mode.set_repo_path(repo_path)
    click.echo("Dev Mode: repo_path set to %s" % repo_path)
