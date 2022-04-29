# Running the API

we are currently targeting 3.6 because it's latest version centos7 can easily install via EPEL.

requirements:
- python3.6+
- pip
- virtualenv

to change some settings, see `Makefile` and write them to `local.mk`.

```sh
# recommend add this var to your bashrc or bash_profile
export PIPENV_VENV_IN_PROJECT=1

make install

# under the hood.
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -U pipenv
.venv/bin/pipenv install
```

run API server.

```sh
make run

# under the hood
.venv/bin/python bin/pipelines server --workspace=test/fixtures/workspace --host 0.0.0.0
```

It runs on port 8888.

## special notes on dependencies update

we now use [pipenv](https://pipenv.pypa.io/en/latest/) to manage dependencies. so no more `requirements.txt`.

please use pipenv to install packages.

```sh
# direct dependency
.venv/bin/pipenv install some-package

# dev time dependency
.venv/bin/pipenv install -d some-dev-package
```

after that, use [pipenv-setup](https://github.com/Madoshakalaka/pipenv-setup) to sync `Pipfile/Pipfile.lock` to `setup.py`. because we still want it
possible to install pipelines via `pip install pipelines` on servers.

```sh
make sync-requirements

## under the hood
# sync Pipfile/Pipfile.lock to setup.py
.venv/bin/pipenv-setup sync

# reformat setup.py
.venv/bin/autopep8 -i -a -a setup.py
```

then commit them all into git.

# Frontend development

see README in app folder.
