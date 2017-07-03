import click
from cli.cli import pass_context


@click.command('ls', short_help='list available recipes')
@click.argument('recipes',nargs=-1)
@click.option('-l', '--long_display', is_flag=True, help='Show option for every recipe')
@pass_context
def cli(ctx, recipes, long_display):
    """
    List available recipes
    - If no argument: list all recipes
    - If argument: find respective integration and list all optinos with versions
    """

    def show_recipes(manifest):
        click.echo(manifest["name"])
        for flavor_name, flavor in manifest["flavors"].iteritems():
            click.echo('  ' + flavor_name + ':  ' + flavor["description"])
            for option_name, option in flavor.get("options", {}).iteritems():
                click.echo('    ' + option_name + "s: " + str(option["values"]))

    # list all recipes
    if not recipes:
        for path, manifest in ctx.recipes_cache.iteritems():
            if long_display:
                show_recipes(manifest)
            else:
                click.echo(manifest["name"])
        return

    # list only specified recipes
    for recipe_name in recipes:
        for path, manifest in ctx.recipes_cache.iteritems():
            if recipe_name == manifest['name']:
                show_recipes(manifest)
