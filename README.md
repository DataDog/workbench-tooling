# Datadog Integration Workbench tooling

This repo holds the tooling for the `Integration Workbench` project. This project aims at enabling all teams to
easily work with agent integrations; for development, testing, support or demos.

Recipes are stored in the [workbench-recipes](https://github.com/DataDog/workbench-recipes/) repo

# Scope of the project

This umbrella project includes:
  - turn-key [recipes](https://github.com/DataDog/workbench-recipes) to run the software our agent integrates with
  - an easy to use [cli tool](cli/), based around [docker-compose](https://docs.docker.com/compose/), to retrieve,
  list and run recipes
  - [autodiscovery](http://docs.datadoghq.com/guides/autodiscovery/) templates for every recipe
  - [standard Vagrant hosts](host/) for fast ramp-up

We chose to go with docker and docker-compose for several reasons:
  - containers allow fast and clean install and removal of software for development / testing purpoes
  - as more and more software projects provide official docker images, we can base our work on these images to reduce
   our maintenance effort
  - relying on the [autodiscovery](http://docs.datadoghq.com/guides/autodiscovery/) feature of the Datadog Agent
  allows for an easier setup workflow

# How to use it

You can either:
  - use one of our [standard Vagrant hosts](host/)
  - directly [run the cli](cli/) on a Linux host
