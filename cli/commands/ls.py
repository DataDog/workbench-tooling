import click
from cli.cli import pass_context


@click.command('ls', short_help='list available recipes')
@click.argument('recipes',nargs=-1)
@pass_context
def cli(ctx, recipes):
    """
    List available recipes
    - If no argument: list all recipes
    - If argument: find respective integration and list all optinos with versions
    """

    def show_recipes(manifest):
        click.echo(manifest["name"])
        for flavor_name, flavor in manifest["flavors"].iteritems():
            click.echo('  %s:  %s' % (flavor_name, flavor["description"]))
            for option_name, option in flavor.get("options", {}).iteritems():
                click.echo("    %s:" % option_name)
                if option.get("values"):
                    click.echo("        possible values: %s" % ' | '.join(option["values"]))
                if option.get("default"):
                    click.echo("        default:  %s" % option["default"])

    # list all recipes
    if not recipes:
        for path, manifest in ctx.recipes_cache.iteritems():
            show_recipes(manifest)
        return

    # list only specified recipes
    for recipe_name in recipes:
        for path, manifest in ctx.recipes_cache.iteritems():
            if recipe_name == manifest['name']:
                show_recipes(manifest)
