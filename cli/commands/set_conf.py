import click
import json
from cli.cli import pass_context
from cli import setting


@click.command('set_conf', short_help='Set a global configuration value')
@click.argument('key')
@click.argument('value')
@pass_context
def cli(ctx, key, value):
    setting.set(ctx, key, value)
