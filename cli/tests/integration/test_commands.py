# stdlib
from copy import deepcopy
import os
import os.path
import unittest
import tempfile
import shutil
import subprocess

# 3rd party
import docker


class TestCommands(unittest.TestCase):
    """
    This test class calls the commands from the shell and checks
    expected results (containers, files...) are here. Far from a
    unit test replacement, but could help make sure we don't break
    standard workflows and don't depend on previous states.

    TODO: use contant classes for paths (after refacto)
    TODO: silence docker-compose & docker outputs
    """
    def __init__(self, *args, **kwargs):
        super(TestCommands, self).__init__(*args, **kwargs)
        self.docker = docker.from_env()
        self.bashenv = deepcopy(os.environ)

    @property
    def config_dir(self):
        return os.path.join(self.bashenv['HOME'], ".config", "DataDog", "workbench")

    @property
    def recipes_dir(self):
        return os.path.join(self.bashenv['HOME'], ".local", "share", "DataDog", "workbench-recipes")

    def setUp(self):
        self.assertEquals(0, len(self.docker.containers.list()), "docker has running containers")
        self.bashenv['HOME'] = tempfile.mkdtemp(prefix='workbench-tests-')

    def tearDown(self):
        try:
            self._call(['workbench', 'recipe', 'stop', '-a'])
        except subprocess.CalledProcessError:
            pass  # Will exit 1 if nothing was running

        self.assertEquals(0, len(self.docker.containers.list()), "lingering docker containers")
        shutil.rmtree(self.bashenv['HOME'])

    def _call(self, cmd):
        return subprocess.check_output(cmd, env=self.bashenv)

    def test_update(self):
        self._call(['workbench', 'recipe', 'update'])

        # Check we cloned from git
        self.assertTrue(os.path.isdir(self.recipes_dir))
        self.assertTrue(os.path.isfile(os.path.join(self.recipes_dir, ".git", "HEAD")))

        # Check we have the redis manifest file
        self.assertTrue(os.path.isfile(os.path.join(self.recipes_dir, "redis", "manifest.yaml")))

    def test_recipe_ls(self):
        self._call(['workbench', 'recipe', 'update'])
        output = self._call(['workbench', 'recipe', 'ls'])

        # Make sure listing the recipes outputs more than 20 lines
        self.assertGreater(output.count('\n'), 20)

    def test_recipe_run(self):
        self._call(['workbench', 'recipe', 'update'])
        self._call(['workbench', 'recipe', 'run', 'redis', '1master-2slaves'])

        self.assertEquals(3, len(self.docker.containers.list()), "should find 3 redis containers")

    def test_recipe_stop(self):
        self._call(['workbench', 'recipe', 'update'])
        self._call(['workbench', 'recipe', 'run', 'redis', '1master-2slaves'])
        self.assertEquals(3, len(self.docker.containers.list()), "should find 3 redis containers")
        self._call(['workbench', 'recipe', 'stop', 'redis:1master-2slaves'])
        self.assertEquals(0, len(self.docker.containers.list()), "should find 0 redis containers")
