# todoist-python - The official Todoist Python API library

## Quick Start

Install with

```bash
pip install todoist-python
```

Official Documentation can be found at
https://todoist-python.readthedocs.io/en/latest/.

## Example Usage

Import the library and try some commands:

```python
$ python
>>> import todoist
>>> api = todoist.TodoistAPI('0123456789abcdef0123456789abcdef01234567')
>>> api.sync()
>>> full_name = api.state['user']['full_name']
>>> print(full_name)
John Doe
>>> for project in api.state['projects']:
...     print(project['name'])
...
Personal
Shopping
Work
Errands
Movies to watch
```

## Building from Source

### Build Project

Requirements:

- Python 2.7+
- PIP: https://pypi.python.org/pypi/pip
- Virtualenv: https://pypi.python.org/pypi/virtualenv

Clone the repo and enter it:

    $ git clone git@github.com:Doist/todoist-python.git ; cd todoist-python

Create an environment:

    $ virtualenv --system-site-packages -p /usr/bin/python2.7 Env

Activate the environment:

    $ source Env/bin/activate

Install the library along with all the dependencies (so far we depend on awesome
requests only):

    $ pip install -e .

### Build Documentation

If you want to build the documentation as well, install some extra packages:

    $ pip install -r doc/requirements.txt

Build the documentation:

    $ (cd doc ; make html)

Read the built documentation by opening:

    doc/_build/html/index.html

## Testing the library

We have a set of tests to ensure we support Python both 2.x and 3.x. To test it
out, please make sure you have python 2.7 and python 3.4 installed in you
system. Then install "tox" either globally (preferred way) or in your local
environment.

    # apt-get install python-tox

or

    $ pip install tox


You will also need to have the `pytest.ini` file. We are providing a
`pytest.ini.sample` that you can copy and paste to create your own
`pytest.ini`. You will need two different tokens (`token` and `token2` keys on
on `pytest.ini`) to be able to run all the tests successfully.

With everything set up, you can just run:

    $ tox
