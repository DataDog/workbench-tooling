import click
from cli.cli import pass_context


@click.command('exec', short_help='exec in a running container')
@click.argument('container_id', nargs=1)
@click.argument('command', nargs=1)
@click.argument('arguments', nargs=-1)
#@click.option('--privileged', default=False)
#@click.option('--detach', '-d', default=False)
#@click.option('--interactive', '-i', default=False)
#@click.option('--tty', '-t', default=False)
@pass_context
def cli(ctx, container_id, command, arguments):
    try:
        ctx.sh("docker exec -it {0} {1} {2}".format(container_id, command, " ".join(arguments)))
    except Exception as e:
        ctx.fail("ERROR while docker exec: {0}".format(e))
