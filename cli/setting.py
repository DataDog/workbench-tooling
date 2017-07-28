import json
import os
import click

import recipes


def init_context(ctx):
    ctx.setting_file = os.path.join(ctx.local_config, "setting.json")
    if not os.path.exists(ctx.setting_file):
        ctx.setting = {"conf_d_path": ctx.conf_d_path}
        with open(ctx.setting_file, "w") as f:
            json.dump(ctx.setting, f)
    else:
        ctx.setting = get(ctx)

def set(ctx, key, value):
    ctx.setting[key] = value
    if key == recipes.DEV_RECIPE_PATH:
        recipes.refresh_context(ctx)
        recipes.update(ctx)

    with open(ctx.setting_file, 'r+') as f:
        data = json.load(f)
        f.seek(0)
        f.truncate()
        data[key] = value
        json.dump(data, f)


def get(ctx):
    with open(ctx.setting_file, 'r') as f:
        return json.load(f)

def display(ctx):
    click.echo("Setting file: %s\n" % ctx.setting_file)

    click.echo("Settings:")
    for k, v in get(ctx).iteritems():
        click.echo("- %s: %s" % (k, v))
