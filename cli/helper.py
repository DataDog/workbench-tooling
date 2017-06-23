# Helper functions for workbench
import os
import yaml
import json
import shutil
import click

# File management
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
    click.echo("Generating cache...")
    try:
        if not os.path.isdir(os.path.dirname(ctx.cache_file)):
            os.makedirs(os.path.dirname(ctx.cache_file))
        with open(ctx.cache_file, 'w') as stream:
            stream.write(json.dumps(read_yamls(ctx.recipes_dir, "manifest.yaml")))
    except Exception as e:
        ctx.fail("ERROR writing cache file {0}".format(e))

def load_cache(ctx):
    if not os.path.exists(ctx.cache_file):
        generate_cache(ctx)
    try:
        with open(ctx.cache_file) as f:
            recipes_cache = json.load(f)
        return(recipes_cache)
    except Exception as e:
        ctx.fail("ERROR while loading cache {0}".format(e))

