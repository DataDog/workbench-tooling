import click
import os
import git
import json
import yaml
import shutil


DEV_RECIPE_PATH = "dev_recipes_path"
MANIFEST_FILENAME = "manifest.yaml"
AUTOCONF_FOLDER_NAME = "auto_conf"

class Recipes(object):

    def __init__(self, ctx):
        self.ctx = ctx
        self.base_recipes_dir = os.path.join(ctx.local_data, "workbench-recipes")
        if not os.path.exists(self.base_recipes_dir):
            os.makedirs(self.base_recipes_dir)

        self.recipes_cache_file = os.path.join(ctx.local_config, "recipes_cache.json")
        if not os.path.exists(self.recipes_cache_file):
            with open(self.recipes_cache_file, "w") as f:
                f.write("{}")

        self.__refresh_context()
        self.recipes_cache = self.__load()

    def display(self):
        click.echo("Recipes dir: %s" % self.recipes_dir)
        click.echo("Dev recipes dir activated: %s" % self.is_custom_recipes_dir)

    def update(self, force=False):
        if not force and self.ctx.state.is_any_running():
            raise Exception("Please stop all running recipes before updating the cache or use -f option at your own risk.")
        self.__refresh_context()
        self.__update_recipes()

    def __refresh_context(self):
        custom_path = self.ctx.setting.get(DEV_RECIPE_PATH)
        if custom_path:
            self.recipes_dir = custom_path
            self.is_custom_recipes_dir = True
        else:
            self.recipes_dir = self.base_recipes_dir
            self.is_custom_recipes_dir = False

    def __update_recipes(self):
        """
        Update/Initializes the local clone of workbench-recipes.

        This will clone or pull the local clone of workbench-recipes and refresh caches
        """

        # custom recipes path: do not "git pull"
        if not self.is_custom_recipes_dir:
            if not os.path.exists(os.path.join(self.recipes_dir, ".git")):
                click.echo('cloning workbench-recipes to %s' % self.recipes_dir)
                git.Repo.clone_from("https://github.com/DataDog/workbench-recipes.git", self.recipes_dir)
            else:
                click.echo('pulling latest changes from workbench-recipes')
                click.echo(git.cmd.Git(self.recipes_dir).pull())
        else:
            click.echo("local workbench-recipes set (%s): skipping 'git pull'" % self.recipes_dir)

        # Regenerate cache
        self.__generate_cache()
        self.__update_auto_confs()

    def __load(self):
        """
        Load the recipe cache.
        """
        if not os.path.exists(self.recipes_cache_file):
            self.__generate_cache()
        try:
            with open(self.recipes_cache_file) as f:
                return json.load(f)
        except Exception as e:
            self.ctx.fail("ERROR while loading cache {0}".format(e))

    def __update_auto_confs(self):
        """
            Search recursively for every auto_conf directory copy them in the master auto_conf_dir.

            auto_conf_dir will be mount in the agent container and use by AutoConf.
        """
        for root, dirs, files in os.walk(self.recipes_dir):
            if root.endswith(AUTOCONF_FOLDER_NAME):
                self.ctx.vlog("found auto_conf dir: %s" % root)
                for f in files:
                    self.ctx.vlog("importing auto_conf: %s" % f)
                    shutil.copyfile(os.path.join(root, f), os.path.join(self.ctx.auto_conf_dir, f))

    def __generate_cache(self):
        """Generate integration cache from yamls"""
        click.echo("Generating recipes cache...")
        try:
            data = self.__read_yamls(self.recipes_dir, MANIFEST_FILENAME)
        except Exception as e:
            self.ctx.fail("ERROR writing cache file: {0}".format(e))
            return
        with open(self.recipes_cache_file, 'w') as stream:
            stream.write(json.dumps(data))
        self.recipes_cache = data

    def __read_yamls(self, path, endswith=".yaml"):
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

    def run(self, recipe_name, flavor_name, search_params):
        recipe_id = "%s:%s" % (recipe_name, flavor_name)
        if self.ctx.state.is_running(recipe_id):
            raise Exception("Recipe for %s is already running" % recipe_id)

        env = {}
        for manifest_path, manifest in self.recipes_cache.iteritems():
            if recipe_name != manifest['name']:
                self.ctx.vlog("Searching for recipe named '%s': ignoring recipe '%s'" % (recipe_name, manifest['name']))
                continue

            flavor = manifest['flavors'].get(flavor_name)
            if not flavor:
                raise Exception("No flavor '%s' for recipe '%s'" % (flavor_name, recipe_name))

            if flavor.get("dev_mode", False):
                env['integrations_core'] = self.ctx.dev_mode.getIntegrationPath()

            for name, option in flavor.get('options', {}).iteritems():
                if 'default' in option:
                    env[name] = option['default']

            for name, required in flavor.get('settings', {}).iteritems():
                value = self.ctx.setting.get(name)
                if value is None and required == "required":
                    raise Exception("Error setting '%s' is required to run %s. See command 'conf set'." % (name, recipe_id))
                if value:
                    env[name] = value

            flavor_options = flavor.get('options', {})
            for option, value in search_params.iteritems():
                if option in flavor_options:
                    if flavor_options[option].get('values') and value not in flavor_options[option]['values']:
                        raise Exception("option '%s' does not offer value %s in recipe %s" % (option, value, recipe_id))
                    env[option] = value
                else:
                    raise Exception("option '%s' does not exist in recipe %s" % (option, recipe_id))

            env_string = ' '.join(['='.join([key, val]) for key, val in env.iteritems()])
            docker_compose_file = os.path.join(manifest_path, flavor['compose_file'])

            cmd = "%s docker-compose -f %s up -d" % (env_string, docker_compose_file)
            # create common network in any case
            try:
                self.ctx.sh("docker network create workbench")
            except:
                pass
            self.ctx.sh(cmd)
            self.ctx.state.add_running(recipe_id, docker_compose_file, env_string)
            return
        raise Exception("No recipe found matching the filter")

    def list(self, recipes):
        """
        List available recipes
        - If no argument: list all recipes
        - If argument: find respective integration and list all optinos with versions
        """
        def show_recipes(manifest):
            click.echo(manifest["name"])
            for flavor_name, flavor in manifest["flavors"].iteritems():
                click.echo('  %s:  %s' % (flavor_name, flavor["description"]))
                for option_name, option in flavor.get("options", {}).iteritems():
                    click.echo("    %s:" % option_name)
                    if option.get("values"):
                        click.echo("        possible values: %s" % ' | '.join(option["values"]))
                    if option.get("default"):
                        click.echo("        default:  %s" % option["default"])

        # list all recipes
        if not recipes:
            for _, manifest in self.recipes_cache.iteritems():
                show_recipes(manifest)
            return

        # list only specified recipes
        for recipe_name in recipes:
            for _, manifest in self.recipes_cache.iteritems():
                if recipe_name == manifest['name']:
                    show_recipes(manifest)
