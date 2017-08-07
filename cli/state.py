import os
import json

import click


class State(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.state_file = os.path.join(ctx.local_config, "state.json")

        # for now we initialize every internal file here
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w") as f:
                f.write('{}')
                self.running = {}
        else:
            with open(self.state_file, 'r') as f:
                try:
                    self.running = json.load(f)
                except ValueError:
                    ctx.vlog("Error while loading internal state: reseting it")
                    self.running = {}
                    self.__save()

    def get(self, key):
        return self.running.get(key)

    def add_running(self, recipe_id, compose_file, options):
        self.running[recipe_id] = {'compose_file': compose_file, 'options': options}
        self.__save()

    def remove_running(self, recipe_id):
        del self.running[recipe_id]
        self.__save()

    def __save(self):
        with open(self.state_file, 'w+') as f:
            f.truncate()
            json.dump(self.running, f)

    def is_running(self, recipe_id):
        return recipe_id in self.running

    def is_any_running(self):
        return bool(self.running)

    def display(self):
        click.echo("State file: %s\n" % self.state_file)
        click.echo("Running recipes:")
        for name, info in self.running.iteritems():
            click.echo("%s:\n\toption: %s" % (name, info['options']))

    def stop(self, recipe_ids):
        for recipe_id in recipe_ids:
            info = self.get(recipe_id)
            if not info:
                raise Exception("%s is not running" % recipe_id)

            self.ctx.sh("%s docker-compose -f %s down -v" % (info['options'], info['compose_file']))
            self.remove_running(recipe_id)

    def stop_all(self):
        self.stop(self.running.keys())
