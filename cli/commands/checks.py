import click
from cli.cli import pass_context


@click.command('checks', short_help='run agent checks for running containers')
@click.argument('container_id', default="agent5_agent5-release_1")
@pass_context
def cli(ctx, container_id):
    try:
        ctx.sh("docker exec -it {0} /opt/datadog-agent/embedded/bin/python /opt/datadog-agent/agent/agent.py info".format(container_id))
    except Exception as e:
        ctx.fail("ERROR while checks: {0}".format(e))
