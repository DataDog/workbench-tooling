import click
from cli.cli import pass_context
from cli import state


@click.command('ps', short_help='List running recipes')
@pass_context
def cli(ctx):
    s = state.get(ctx)
    if s is None or len(s['running']) == 0:
        ctx.fail("No recipes are running")

    for recipe_id, info in s['running'].iteritems():
        click.echo("\nRecipe %s:" % recipe_id)
        ctx.sh("%s docker-compose -f %s ps" % (info['options'], info['compose_file']))
