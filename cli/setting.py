import json
import os

import recipes


def init_context(ctx):
    ctx.setting_file = os.path.join(ctx.local_config, "setting.json")
    if not os.path.exists(ctx.setting_file):
        with open(ctx.setting_file, "w") as f:
            f.write('{}')
        ctx.setting = {}
    else:
        ctx.setting = get(ctx)

def set(ctx, key, value):
    with open(ctx.setting_file, 'r+') as f:
        data = json.load(f)
        f.seek(0)
        f.truncate()
        data[key] = value
        json.dump(data, f)
    ctx.setting[key] = value

    if key == recipes.DEV_RECIPE_PATH:
        recipes.refresh_context(ctx)
        recipes.update(ctx)

def get(ctx):
    with open(ctx.setting_file, 'r') as f:
        return json.load(f)
