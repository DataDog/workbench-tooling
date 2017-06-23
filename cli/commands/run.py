import click
import os
from cli.cli import pass_context
from cli import state


@click.command('run', short_help='Run a recipe')
@click.argument('recipe_name')
@click.argument('flavor_name')
@click.argument('filters', nargs=-1)
@pass_context
def cli(ctx, recipe_name, flavor_name, filters):
    search = {}
    for f in filters:
        if not "=" in f:
            ctx.fail("'%s' should be set to a filter format 'key=value'" % f)
        k, v = f.split("=", 1)
        search[k] = v
    recipe_id = "%s:%s" % (recipe_name, flavor_name)
    if state.is_running(ctx, recipe_id):
        ctx.fail("Recipe for %s is already running" % recipe_id)

    env = {}

    for manifest_path, manifest in ctx.recipes_cache.iteritems():
        if recipe_name != manifest['name']:
            ctx.vlog("Searching for recipe named '%s': ignoring recipe '%s'" % (recipe_name, manifest['name']))
            continue

        for name, flavor in manifest['flavors'].iteritems():
            if flavor_name != name:
                ctx.vlog("Searching for flavor named '%s': ignoring flavor '%s'" % (flavor_name, name))
                continue

            if "options" in flavor:
                for name, option in flavor['options'].iteritems():
                    if 'default' in option:
                        env[name] = option['default']

                for option, value in  search.iteritems():
                    if option in flavor['options']:
                        if not value in flavor['options'][option]['values']:
                            ctx.fail("option '%s' does not offer value %s in recipe %s" % (option, value, recipe_id))
                        env[option] = value
                    else:
                        ctx.fail("option '%s' does not exist in recipe %s" % (option, recipe_id))

            env_string = ' '.join(['='.join([k,v]) for k, v in env.iteritems()])
            docker_compose_file = os.path.join(ctx.recipes_dir, manifest_path, flavor['compose_file'])

            cmd = "%s docker-compose -f %s up -d" % (env_string, docker_compose_file)

            # create common network in any case
            try:
                ctx.sh("docker network create workbench")
            except:
                pass
            ctx.sh(cmd)
            state.add_running_compose(ctx, recipe_id, docker_compose_file, env_string)
            return
    print "No recipe found matching the filter"
