import click
from cli.cli import pass_context


@click.group("conf")
def cli():
    """Manages Workbench configuration."""

@cli.command('ls', short_help='Show global configuration')
@pass_context
def ls(ctx):
    ctx.setting.display()


@cli.command('remove', short_help='Remove a value from the global configuration')
@click.argument('key')
@pass_context
def remove(ctx, key):
    try:
        ctx.setting.remove(key)
    except Exception as e:
        ctx.fail(e)


@cli.command('set', short_help='Set a global configuration value')
@click.argument('key')
@click.argument('value')
@pass_context
def set(ctx, key, value):
    try:
        ctx.setting.set(key, value)
    except Exception as e:
        ctx.fail(e)
