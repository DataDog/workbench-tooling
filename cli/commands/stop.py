import click
import os
from cli.cli import pass_context
from cli import state


@click.command('stop', short_help='Stop a recipe')
@click.argument('recipe_ids', nargs=-1)
@click.option('-a', is_flag=True, help='Stop every running recipe.')
@pass_context
def cli(ctx, recipe_ids, a):
    s = state.get(ctx)
    if len(s['running']) == 0:
        ctx.fail("No recipes are running")

    if a:
        for recipe_id, info in s['running'].iteritems():
            ctx.sh("%s docker-compose -f %s down" % (info['options'], info['compose_file']))
            state.remove_running_compose(ctx, recipe_id)
        return

    if not recipe_ids:
        click.echo("Provide at least one recipe_id or use '-a' option.\n")
        click.echo("running recipe:\n- %s" % "\n- ".join(s['running'].keys()))
        return

    for recipe_id in recipe_ids:
        if recipe_id not in s['running']:
            ctx.fail("%s is not running" % recipe_id)

        info = s['running'][recipe_id]
        ctx.sh("%s docker-compose -f %s down" % (info['options'], info['compose_file']))
        state.remove_running_compose(ctx, recipe_id)
