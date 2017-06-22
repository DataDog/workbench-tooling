# Helper functions for workbench
import os
import yaml

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

