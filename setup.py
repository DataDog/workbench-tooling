from setuptools import setup

setup(
    name='workbench',
    version='1.0',
    packages=['cli', 'cli.commands'],
    include_package_data=True,
    install_requires=[
        'click',
        'GitPython',
    ],
    entry_points='''
        [console_scripts]
        workbench=cli.cli:cli
    ''',
)
