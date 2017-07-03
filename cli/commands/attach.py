import click
from cli.cli import pass_context


@click.command('attach', short_help='attach to a running container')
@click.argument('container_id', nargs=1)
@pass_context
def cli(ctx, container_id):
    try:
        ctx.sh("docker exec -it {0} /bin/bash".format(container_id))
    except Exception as e:
        ctx.fail("ERROR while docker exec: {0}".format(e))
