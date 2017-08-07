import click
from cli.cli import pass_context


@click.group("recipe")
def cli():
    """Manages Workbench recipes."""


@cli.command('run', short_help='Run a recipe')
@click.argument('recipe_name')
@click.argument('flavor_name')
@click.argument('filters', nargs=-1)
@pass_context
def run(ctx, recipe_name, flavor_name, filters):
    search = {}
    for f in filters:
        if "=" not in f:
            ctx.fail("'%s' should be set to a filter format 'key=value'" % f)
        k, v = f.split("=", 1)
        search[k] = v

    try:
        ctx.recipes.run(recipe_name, flavor_name, search)
    except Exception as e:
        ctx.fail(e)


@cli.command('stop', short_help='Stop a recipe')
@click.argument('recipe_ids', nargs=-1)
@click.option('-a', is_flag=True, help='Stop every running recipe.')
@pass_context
def stop(ctx, recipe_ids, a):
    if not ctx.state.is_any_running():
        ctx.fail("No recipes are running")

    if a:
        ctx.state.stop_all()
    elif not recipe_ids:
        click.echo("Provide at least one recipe_id or use '-a' option.\n")
        click.echo("running recipe:\n- %s" % "\n- ".join(ctx.state.running.keys()))
    else:
        ctx.state.stop(recipe_ids)


@cli.command('ps', short_help='List running recipes')
@click.argument('recipe_id')
@click.option('-f', '--follow', is_flag=True, help='Follow log output')
@pass_context
def logs(ctx, recipe_id, follow):
    info = ctx.state.get(recipe_id)
    if not info:
        ctx.fail("Recipe %s isn't running" % recipe_id)

    ctx.sh("%s docker-compose -f %s logs %s" % (info['options'], info['compose_file'], '-f' if follow else ''))


@cli.command('ps', short_help='List running recipes')
@pass_context
def ps(ctx):
    if not ctx.state.is_any_running():
        ctx.fail("No recipes are running")

    for recipe_id, info in ctx.state.running.iteritems():
        click.echo("\nRecipe %s" % recipe_id)
        ctx.sh("%s docker-compose -f %s ps" % (info['options'], info['compose_file']))


@cli.command('exec', short_help='exec in a running container')
@click.argument('container_id', nargs=1)
@click.argument('command', nargs=1)
@click.argument('arguments', nargs=-1)
#@click.option('--privileged', default=False)
#@click.option('--detach', '-d', default=False)
#@click.option('--interactive', '-i', default=False)
#@click.option('--tty', '-t', default=False)
@pass_context
def exec_command(ctx, container_id, command, arguments):
    try:
        ctx.sh("docker exec -it {0} {1} {2}".format(container_id, command, " ".join(arguments)))
    except Exception as e:
        ctx.fail("ERROR while docker exec: {0}".format(e))


@cli.command('attach', short_help='attach to a running container')
@click.argument('container_id', nargs=1)
@pass_context
def attach(ctx, container_id):
    try:
        ctx.sh("docker exec -it {0} /bin/bash".format(container_id))
    except Exception as e:
        ctx.fail("ERROR while docker exec: {0}".format(e))


@cli.command('checks', short_help='run agent checks for running containers')
@click.argument('container_id', default="agent5_agent5-release_1")
@pass_context
def checks(ctx, container_id):
    try:
        ctx.sh("docker exec -it {0} /opt/datadog-agent/embedded/bin/python /opt/datadog-agent/agent/agent.py info".format(container_id))
    except Exception as e:
        ctx.fail("ERROR while checks: {0}".format(e))


@cli.command('ls', short_help='list available recipes')
@click.argument('recipes',nargs=-1)
@pass_context
def ls(ctx, recipes):
    ctx.recipes.list(recipes)

@cli.command('update', short_help='Update/Initializes the local clone of workbench-recipes')
@click.option('-f', '--force', is_flag=True, help='Force the update even if some recipes are running')
@pass_context
def update(ctx, force):
    """
    Update/Initializes the local clone of workbench-recipes.

    This will clone or pull the local clone of workbench-recipes and refresh caches
    """
    try:
        ctx.recipes.update(force=force)
    except Exception as e:
        ctx.fail(e)
