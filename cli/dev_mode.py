import click
import os


INTEGRATION_CONF_KEY = "integrations_core_path"

class DevMode(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.base_integration = os.path.join(ctx.local_data, "integrations")
        if not os.path.exists(self.base_integration):
            os.makedirs(self.base_integration)

    def __get_integration_path(self, integration_name):
        return os.path.join(self.base_integration, integration_name+".py")

    def deactivate_integration(self, integration_names):
        for integration_name in integration_names:
            click.echo("Deactivating %s" % integration_name)
            os.unlink(self.__get_integration_path(integration_name))

    def deactivate_all_integration(self):
        for integration_name in os.listdir(self.base_integration):
            self.deactivate_integration(integration_name.split(".")[0])

    def activate_integration(self, integration_name):
        if os.path.exists(self.__get_integration_path(integration_name)):
            raise Exception("integration '%s' is already activated" % integration_name)

        core = self.ctx.setting.get(INTEGRATION_CONF_KEY)
        if core:
            check_path = os.path.join(core, integration_name, "datadog_checks", integration_name, integration_name+".py")
            if os.path.isfile(check_path):
                os.link(check_path, self.__get_integration_path(integration_name))
            else:
                raise Exception("No integration name '%s' in %s (file not found '%s')" % (integration_name, core, check_path))
        else:
            raise Exception("Please first set the path to your local integrations repository, use: dev_mode set_repo_path")

    def display(self):
        core = self.ctx.setting.get(INTEGRATION_CONF_KEY)

        click.echo("%s: %s" % (INTEGRATION_CONF_KEY, core))
        click.echo("Local instegration path: %s\n" % self.base_integration)

        self.list_integration()

    def list_integration(self):
        click.echo("Activated integration:")
        for i in os.listdir(self.base_integration):
            click.echo("- %s" % i)

    def getIntegrationPath(self):
        return self.base_integration

    def set_repo_path(self, repo_path):
        return self.ctx.setting.set(INTEGRATION_CONF_KEY, repo_path)
