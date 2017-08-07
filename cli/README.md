# Installation
- make sure you have `python`, `python-pip`, `docker-compose` installed
- run `$ pip install .`   
  (optionally in a venv by running `mkdir venv && virtualenv venv && . venv/bin/activate`. use then `deactivate` to exit venv)
- run `$ workbench recipe update`
- run `$ workbench` for usage help

# Usage

## Recipe

To run, stop and manage recipes

```
$ workbench recipe ls
mongodb
elasticsearch

$ workbench recipe ls mongodb
mongodb
  replicas3:  3 mongo replicaset with dummy data
    versions: [u'3.0', u'3.2', u'3.4', u'3.5']
  standalone:  One mongo instance with dummy data
    versions: [u'3.0', u'3.2', u'3.4', u'3.5']

$ workbench recipe run mongodb standalone version=3.0
[…]
Creating mongodb_mongo-standalone_1 ... done

$ workbench recipe ps

Recipe mongodb:standalone:
           Name                         Command               State     Ports
-------------------------------------------------------------------------------
mongodb_mongo-standalone_1   docker-entrypoint.sh mongo ...   Up      27017/tcp

$ workbench recipe attach mangodb:standalone

$ workbench recipe stop mangodb:standalone
```

## Conf

To change the configuration. Note that configuration info are available to
recipes manifest.

```
$> workbench conf set key value
$> workbench conf ls
key: value
$> workbench conf remove key
```

### Agent API key

You can set the Agent API key used by some containers (depending on their manifest, see `settings` section).

```
$> workbench conf set dd_api_key 123456789
$> workbench conf ls
dd_api_key: 123456789

```

### Custom recipes location

By default the `update` command will clone
[recipes](https://github.com/DataDog/workbench-recipes) locally
(`~/.local/share/DataDog/workbench-recipes/`) and pull the latest changes from
**master**. You can overwrite that localtion to use a local clone (for
development purpose). If you do so **workbench** will skip the `git pull` part
of the update command and only update its recipes cache and auto_conf templates.

```
$> workbench conf set dev_recipes_path ~/dev/workbench-recipes
local workbench-recipes set (/home/user/dev/workbench-recipes): skipping 'git pull'
Generating recipes cache...
$> workbench conf ls
dev_recipes_path: /home/user/dev/workbench-recipes
```

## Dev mode

Dev mode is intended to ease development of integration.

Dev mode will:
- Use a local clone of
  [integrations-core](https://github.com/DataDog/integrations-core) or
  [integrations-extras](https://github.com/DataDog/integrations-extras) and
  create a local `checks.d` folder to be mounted in agent containers. This allows
  you to use local integration inside agent recipes. The path of this folder is
  available in docker-compose file under the environment variable
  `integrations_core`.
- _more to come_


To activate it first set then path to your local integrations repo:

```
$> workbench dev_mode set_repo_path /path/to/integrations-repo
Dev Mode: repo_path set to /path/to/integrations-repo
```

Then you can activate specific integrations:

```
$> workbench dev_mode activate_integration nginx
Activating nginx
$> workbench dev_mode activate_integration apache
Activating apache
```

You can list activated integrations:

```
$> workbench dev_mode ls
Activated integration:
- apache.py
- nginx.py
```

And deactivate integrations.

By names:
```
$> workbench dev_mode deactivate_integration apache nginx
Deactivating apache
Deactivating nginx
```

Or everyone of them:

```
$> workbench dev_mode deactivate_integration -a
Deactivating apache
Deactivating nginx
```

To use it in recipes see [Workbench Recipes](https://github.com/DataDog/workbench-recipes#dev-mode).

## Lint

To lint recipes currently used by **Workbench** (see [Custom recipes location](custom-recipes-location)).

```
$> workbench Lint
All OK in 11 manifests and 9 auto_conf templates
```

or any folder:

```
$> workbench Lint /path/to/recipes
All OK in 11 manifests and 9 auto_conf templates
```

## Prune

Run `docker system prune`

```
$> workbench prune
WARNING! This will remove:
- all stopped containers
- all volumes not used by at least one container
- all networks not used by at least one container
- all dangling images
Are you sure you want to continue? [y/N] y
Deleted Volumes:
338c98d38ffc9c719e309b878d682e54500e33a9c9ae2f040f771b592ce0f469
9974cb3dccab33454501954ec35d62516704e26a35add810fd799f04be042c79
f5a3b658a9534a399014cc2120715537e0ceed3191bb1853c1b2adcc0726104f

Deleted Networks:
workbench

Total reclaimed space: 5.213MB

```

## Reset

This command stop all recipes, disable every integration in dev_mode and remove
all local setting files. This will reset the workbench as it was after a fresh
Installation.


```
$> workbench reset
Stopping all recipes
Reseting dev_mode
Removing local file
- /home/hush-hush/.config/DataDog/workbench
- /home/hush-hush/.local/share/DataDog
```
