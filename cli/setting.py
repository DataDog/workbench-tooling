import json
import os
import click
import recipes


class Setting(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.setting_file = os.path.join(ctx.local_config, "setting.json")
        if not os.path.exists(self.setting_file):
            self.data = {"conf_d_path": ctx.conf_d_path}
            with open(self.setting_file, "w+") as f:
                json.dump(self.data, f)
        else:
            with open(self.setting_file, 'r') as f:
                self.data = json.load(f)

    def set(self, key, value):
        self.data[key] = value
        if key == recipes.DEV_RECIPE_PATH:
            if self.ctx.state.is_any_running():
                raise Exception("Some recipes are running, please stop them before running an update")

            self.ctx.recipes.update()
        self.save()

    def remove(self, key):
        if key in self.data:
            self.data.pop(key)
            if key == recipes.DEV_RECIPE_PATH:
                if self.ctx.state.is_any_running():
                    raise Exception("Some recipes are running, please stop them before running an update")
                self.ctx.recipes.update()
            self.save()

    def save(self):
        with open(self.setting_file, 'r+') as f:
            f.truncate()
            json.dump(self.data, f)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def display(self):
        click.echo("Setting file: %s\n" % self.setting_file)

        click.echo("Settings:")
        for k, v in self.data.iteritems():
            click.echo("- %s: %s" % (k, v))
