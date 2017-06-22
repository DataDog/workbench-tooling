import click
import os
from cli.cli import pass_context
from cli.helper import State


@click.command('ps', short_help='List running recipes')
@pass_context
def cli(ctx):
    state = State.get_state(ctx)
    if len(state['running']) == 0:
        ctx.fail("No recipes are running")

    for recipe_id, info in state['running'].iteritems():
        click.echo("\nRecipe %s:" % recipe_id)
        ctx.sh("%s docker-compose -f %s ps" % (info['options'], info['compose_file']))
