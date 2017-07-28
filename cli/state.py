import os
import json

import click


def init_context(ctx):
    ctx.state_file = os.path.join(ctx.local_config, "state.json")

    # for now we initialize every internal file here
    if not os.path.exists(ctx.state_file):
        with open(ctx.state_file, "w") as f:
            f.write('{"running": {}}')

def get(ctx):
    with open(ctx.state_file, 'r') as f:
        try:
            return json.load(f)
        except ValueError:
            ctx.vlog("Error while loading internal state: reseting it")
            return {'running': {}}

def add_running_compose(ctx, recipe_id, compose_file, options):
    entry = {'compose_file': compose_file, 'options': options}

    data = get(ctx)
    with open(ctx.state_file, 'w+') as f:
        f.truncate()
        if 'running' not in data:
            data['running'] = {}
        data['running'][recipe_id] = entry
        json.dump(data, f)

def remove_running_compose(ctx, recipe_id):
    with open(ctx.state_file, 'r+') as f:
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

def is_running(ctx, recipe_id):
    state = get(ctx)
    if not state:
        return False
    return recipe_id in state.get('running', {})

def display(ctx):
    click.echo("State file: %s\n" % ctx.state_file)
    s = get(ctx)
    click.echo("Running recipes:")
    for name, info in s['running'].iteritems():
        click.echo("%s:\n\toption: %s" % (name, info['options']))
