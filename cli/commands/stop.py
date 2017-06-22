import click
import os
from cli.cli import pass_context
from cli.helper import State


@click.command('stop', short_help='Stop a recipe')
@click.argument('recipe_ids', nargs=-1)
@click.option('-a', is_flag=True, help='Stop every running recipe.')
@pass_context
def cli(ctx, recipe_ids, a):
    state = State.get_state(ctx)
    if len(state['running']) == 0:
        ctx.fail("No recipes are running")

    if a:
        for recipe_id, info in state['running'].iteritems():
            ctx.sh("%s docker-compose -f %s down" % (info['options'], info['compose_file']))
            State.remove_running_compose(ctx, recipe_id)
        return

    if not recipe_ids:
        click.echo("At least one recipe_id is needed.\n")
        click.echo("running recipe:\n- %s" % "\n- ".join(state['running'].keys()))
        return

    for recipe_id in recipe_ids:
        if recipe_id not in state['running']:
            ctx.fail("%s is not running" % recipe_id)

        ctx.sh("docker-compose -f %s down" % state['running'][recipe_id])
        State.remove_running_compose(ctx, recipe_id)
