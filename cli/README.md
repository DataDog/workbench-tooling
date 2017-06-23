# Install
- make sure you have `python`, `python-pip`, `docker-compose` installed
- run `$ pip install .` 
  (optionally in a venv by running `mkdir venv && virtualenv venv && . venv/bin/activate`. use then `deactivate` to exit venv)
- run `$ workbench update`

# Usage

```
$ workbench ls-int
mongodb
elasticsearch

$ workbench ls-int mongodb
mongodb
  replicas3:  3 mongo replicaset with dummy data
    versions: [u'3.0', u'3.2', u'3.4', u'3.5']
  standalone:  One mongo instance with dummy data
    versions: [u'3.0', u'3.2', u'3.4', u'3.5']

$ workbench run mongodb standalone version=3.0
[…]
Creating mongodb_mongo-standalone_1 ... done

$ workbench ps

Recipe mongodb:standalone:
           Name                         Command               State     Ports
-------------------------------------------------------------------------------
mongodb_mongo-standalone_1   docker-entrypoint.sh mongo ...   Up      27017/tcp

$ workbench attach mangodb:standalone

$ workbench stop mangodb:standalone
```
