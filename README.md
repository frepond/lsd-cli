# LSD CLI

Leapsight Semantic Dataspace Command Line Tool

## Install

    $ pip install lsd-cli

## Usage

To use it simply run:

    $ lsd-cli --help


## Development

If you want to test this tool and contribute to the development clone this repository
and start submitting your changes.

Simply run the following to install it locally:

    $ pip install -e .

Then just start de client:

    $ lsd-cli

## Build & Publish

    $ pypy3 setup.py build bdist_wheel

    $ twine upload -u <USERNAME> -p <PASSWORD> dist/lsd_cli-<VERSION>-py2.py3-none-any.whl

## Taste some awesome lsd-cli!

Welcome screen:

![Welcome](images/welcome.png)

Help screen:

![Help](images/help.png)

A beautifully formated query result:

![Query](images/query.png)
