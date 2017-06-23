import json

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
