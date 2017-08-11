import click
from cli.cli import pass_context
from cli import state


@click.command('ps', short_help='List running recipes')
@click.argument('recipe_id')
@click.option('-f', '--follow', is_flag=True, help='Follow log output')
@pass_context
def cli(ctx, recipe_id, follow):
    s = state.get(ctx)

    if s:
        info = s['running'].get(recipe_id)
        if not info:
            ctx.fail("Recipe %s isn't running" % recipe_id)

        ctx.sh("%s docker-compose -f %s logs %s" % (info['options'], info['compose_file'], '-f' if follow else ''))