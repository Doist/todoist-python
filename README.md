# todoist-python - The official Todoist Python API library

## How to get started

Requirements:

* Python 2.7+
* PIP: https://pypi.python.org/pypi/pip
* Virtualenv: https://pypi.python.org/pypi/virtualenv

Clone the repo:

    $ git clone git@github.com:Doist/todoist-python.git

Create an environment:

    $ virtualenv --system-site-packages -p /usr/bin/python2.7 Env

Activate the environment:

    $ source Env/bin/activate

Install the library along with all the dependencies (so far we depend on awesome
requests only):


    $ pip install -e .


If you want to build the documentation as well, install some extra packages:

    $ pip install -r doc/requirements.txt

Build the documentation:

    $ (cd doc ; make html)

Read the built documentation by opening:

    doc/_build/html/index.html

Import the library and try some commands:

```python
$ python
>>> import todoist
>>> api = todoist.TodoistAPI()
>>> user = api.login('john.doe@gmail.com', 'secret')
>>> print(user['full_name'])
John Doe
>>> response = api.sync(resource_types=['all'])
>>> for project in response['Projects']:
...     print(project['name'])
...
Personal
Shopping
Work
Errands
Movies to watch
```


## Testing the library

We have a set of tests to ensure we support Python both 2.x and 3.x.  To test
it out, please make sure you have python 2.7 and python 3.4 installed in you
system. Then install "tox" either globally (preferred way) or in your local
environment.

    # apt-get install python-tox

or

    $ pip install tox

Then just type

    $ tox
