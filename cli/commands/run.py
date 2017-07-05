import click
import os
from cli.cli import pass_context
from cli import state
from cli import setting


@click.command('run', short_help='Run a recipe')
@click.argument('recipe_name')
@click.argument('flavor_name')
@click.argument('filters', nargs=-1)
@pass_context
def cli(ctx, recipe_name, flavor_name, filters):
    search = {}
    for f in filters:
        if "=" not in f:
            ctx.fail("'%s' should be set to a filter format 'key=value'" % f)
        k, v = f.split("=", 1)
        search[k] = v
    recipe_id = "%s:%s" % (recipe_name, flavor_name)
    if state.is_running(ctx, recipe_id):
        ctx.fail("Recipe for %s is already running" % recipe_id)

    settings = setting.get(ctx)
    env = {}

    for manifest_path, manifest in ctx.recipes_cache.iteritems():
        if recipe_name != manifest['name']:
            ctx.vlog("Searching for recipe named '%s': ignoring recipe '%s'" % (recipe_name, manifest['name']))
            continue

        for name, flavor in manifest['flavors'].iteritems():
            if flavor_name != name:
                ctx.vlog("Searching for flavor named '%s': ignoring flavor '%s'" % (flavor_name, name))
                continue

            for name, option in flavor.get('options', {}).iteritems():
                if 'default' in option:
                    env[name] = option['default']

            for name, required in flavor.get('settings', {}).iteritems():

                # hack: we should merge ctx info and setting somehow
                if name == 'conf_d_path':
                    env['conf_d_path'] = ctx.conf_d_dir
                    continue

                if name not in settings and required:
                    ctx.fail("Error setting '%s' is required to run %s. See command 'set_conf'." % (name, recipe_id))
                value = settings.get(name)
                if value:
                    env[name] = value

            flavor_options = flavor.get('options', {})
            for option, value in search.iteritems():
                if option in flavor_options:
                    if flavor_options[option].get('values') and value not in flavor_options[option]['values']:
                        ctx.fail("option '%s' does not offer value %s in recipe %s" % (option, value, recipe_id))
                    env[option] = value
                else:
                    ctx.fail("option '%s' does not exist in recipe %s" % (option, recipe_id))

            env_string = ' '.join(['='.join([key, val]) for key, val in env.iteritems()])
            docker_compose_file = os.path.join(manifest_path, flavor['compose_file'])

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
