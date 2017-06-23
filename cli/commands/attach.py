import click
import os
from cli.cli import pass_context

@click.command('attach', short_help='attach to a running container')
@click.argument('container_id', nargs=1)
@pass_context
def cli(ctx, container_id, docker_options):
    ctx.sh("docker exec -it {0} /bin/bash".format(container_id)
