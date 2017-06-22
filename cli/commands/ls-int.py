import click
import cli.helper
from cli import helper
from cli.cli import pass_context

@click.command('ls-int', short_help='list available integrations')
@click.argument('integrations',nargs= -1)
@pass_context
def cli(ctx, integrations):
    """List available integrations
    - If no argument: list all integrations
    - If argument: find respective integration and list all optinos with versions"""
    yamls = helper.read_yamls(ctx.recipes_dir)
    if integrations:
        for integration in integrations:
            for int_yaml_name, int_yaml in yamls.iteritems():
                if int_yaml_name == integration:
                    click.echo(int_yaml["name"])
                    for flavor_name, flavor in int_yaml["flavors"].iteritems():
                        click.echo('  ' + flavor_name+ ':  ' + flavor["description"])
                        for option_name, option in flavor["options"].iteritems():
                            click.echo('    ' + option_name + "s: " + str(option["values"]))
    else:
        for int_yaml_name, int_yaml in yamls.iteritems():
            click.echo(int_yaml["name"])
