import click
import os
import git
import json
import yaml
import shutil
import errno

import state


DEV_RECIPE_PATH = "dev_recipes_path"

def init_context(ctx):
    ctx.base_recipes_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "DataDog", "workbench-recipes")
    try:
        os.makedirs(ctx.base_recipes_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    ctx.recipes_cache_file = os.path.join(ctx.local_config, "recipes_cache.json")
    if not os.path.exists(ctx.recipes_cache_file):
        with open(ctx.recipes_cache_file, "w") as f:
            f.write("{}")

    refresh_context(ctx)
    ctx.recipes_cache = load(ctx)

def refresh_context(ctx):
    custom_path = ctx.setting.get(DEV_RECIPE_PATH)
    if custom_path:
        ctx.recipes_dir = custom_path
        ctx.is_custom_recipes_dir = True
    else:
        ctx.recipes_dir = ctx.base_recipes_dir
        ctx.is_custom_recipes_dir = False

def update(ctx):
    """
    Update/Initializes the local clone of workbench-recipes.

    This will clone or pull the local clone of workbench-recipes and refresh caches
    """

    s = state.get(ctx)
    if len(s['running']) > 0:
        ctx.fail("Some recipes are running, please stop them before running an update")

    # custom recipes path: do not "git pull"
    if not ctx.is_custom_recipes_dir:
        if not os.path.exists(os.path.join(ctx.recipes_dir, ".git")):
            click.echo('cloning workbench-recipes to %s' % ctx.recipes_dir)
            git.Repo.clone_from("https://github.com/DataDog/workbench-recipes.git", ctx.recipes_dir)
        else:
            click.echo('pulling latest changes from workbench-recipes')
            click.echo(git.cmd.Git(ctx.recipes_dir).pull())
    else:
        click.echo("local workbench-recipes set (%s): skipping 'git pull'" % ctx.recipes_dir)

    # Regenerate cache
    generate_cache(ctx)
    update_auto_confs(ctx)

def load(ctx):
    if not os.path.exists(ctx.recipes_cache_file):
        generate_cache(ctx)
    try:
        with open(ctx.recipes_cache_file) as f:
            return json.load(f)
    except Exception as e:
        ctx.fail("ERROR while loading cache {0}".format(e))

def update_auto_confs(ctx):
    """
        Search recursively for every auto_conf directory copy them in the master auto_conf_dir.

        auto_conf_dir will be mount in the agent container and use by AutoConf.
    """
    for root, dirs, files in os.walk(ctx.recipes_dir):
        if root.endswith("auto_conf"):
            ctx.vlog("found auto_conf dir: %s" % root)
            for f in files:
                ctx.vlog("importing auto_conf: %s" % f)
                shutil.copyfile(os.path.join(root, f), os.path.join(ctx.auto_conf_dir, f))

def generate_cache(ctx):
    """Generate integration cache from yamls"""
    click.echo("Generating recipes cache...")
    try:
        data = read_yamls(ctx.recipes_dir, "manifest.yaml")
    except Exception as e:
        ctx.fail("ERROR writing cache file: {0}".format(e))
        return
    with open(ctx.recipes_cache_file, 'w') as stream:
        stream.write(json.dumps(data))
    ctx.recipes_cache = data

def read_yamls(path, endswith=".yaml"):
    """Read recursively all yaml files in directory path and returns a dictionnary"""
    yamls = {}
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(endswith):
                    with open(os.path.join(root, name)) as stream:
                        try:
                            integration_yaml = yaml.load(stream)
                            yamls[root] = integration_yaml
                        except yaml.YAMLError as e:
                            click.echo('Error in YAML file: {0}'.format(e))
                            raise
                        except Exception as e:
                            click.echo('Error while parsing the YAML: {0}'.format(e))
                            raise
    except os.error as err:
        click.echo("ERROR while listing integrations: {0}:".format(err))
    return yamls

def display(ctx):
    click.echo("Recipes dir: %s" % ctx.recipes_dir)
    click.echo("Dev recipes dir activated: %s" % ctx.is_custom_recipes_dir)
