# DATADOG HACKATHLON PROJECT

# Datadog workbench tooling

This repo holds the tooling for the `Datadog workbench` project. This project aims at enabling all teams to easily work with containerized software.

# Repository structure

- host is for host systems (vagrants / terraform / ...)


Recipes are stored in the workbench-recipes repo

# Test the CLI

```
$ mkdir venv
$ virtualenv venv
$ . ./venv/bin/activate
$ pip install .
$ workbench --help
```

# Add bash auto-complete to CLI
```bash
source workbench-complete.sh
```
