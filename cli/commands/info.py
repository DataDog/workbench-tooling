import click
from cli.cli import pass_context


@click.command('info')
@pass_context
def cli(ctx):
    click.echo('workbench is a small tool for easily running Datadog agent and integrations in containers with different setups')

