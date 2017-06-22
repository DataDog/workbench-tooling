# Helper functions for workbench
import os
import yaml
import json
import click

# File management
def read_yamls(path):
    """Read recursively all yaml files in directory path and returns a dictionnary"""
    yamls = {}
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(("manifest.yaml", ".yml")):
                    with open(root + '/' + name) as stream:
                        try:
                            integration_yaml = yaml.load(stream)
                            yamls[integration_yaml["name"]] = integration_yaml
                        except yaml.YAMLError as e:
                            print('Error in YAML file: {0}'.format(e))
                            raise
                        except Exception as e:
                            print('Error while parsing the YAML: {0}'.format(e))
                            raise
    except os.error as err:
        print("ERROR while listing integrations: {0}:".format(err))
    return yamls

def generate_cache(ctx):
    """Generate integration cache from yamls"""
    click.echo("Generating cache...")
    try:
        if not os.path.isdir(os.path.dirname(ctx.cache_file)):
            os.makedirs(os.path.dirname(ctx.cache_file))
        with open(ctx.cache_file, 'w') as stream:
            stream.write(json.dumps(read_yamls(ctx.recipes_dir)))
    except Exception as e:
        print("ERROR writing cache file {0}".format(e))

def load_cache(ctx):
    if not os.path.exists(ctx.cache_file):
        generate_cache(ctx)
    try:
        with open(ctx.cache_file) as f:
            recipes_cache = json.load(f)
        return(recipes_cache)
    except Exception as e:
        print("ERROR while loading cache {0}".format(e))

class State(object):

    @staticmethod
    def get_state(ctx):
        if not os.path.exists(ctx.state_path):
            return None

        with open(ctx.state_path, 'r') as f:
            try:
                return json.load(f)
            except ValueError:
                ctx.vlog("Error while loading internal state: reseting it")
                return {'running': {}}

    @staticmethod
    def add_running_compose(ctx, recipe_id, compose_file):
        if not os.path.exists(ctx.state_path):
            with open(ctx.state_path, 'w+') as f:
                json.dump({'running': {recipe_id: compose_file}}, f)
                return

        data = State.get_state(ctx)
        with open(ctx.state_path, 'w+') as f:
            f.truncate()
            if 'running' not in data:
                data['running'] = {}
            data['running'][recipe_id] = compose_file
            json.dump(data, f)

    @staticmethod
    def remove_running_compose(ctx, recipe_id):
        if not os.path.exists(ctx.state_path):
            return

        with open(ctx.state_path, 'r+') as f:
            try:
                data = json.load(f)
            except ValueError:
                return

            if 'running' not in data:
                return
            del data['running'][recipe_id]

            f.seek(0)
            f.truncate()
            json.dump(data, f)

    @staticmethod
    def is_running(ctx, recipe_id):
        state = State.get_state(ctx)
        if not state:
            return False
        return recipe_id in state.get('running', {})
