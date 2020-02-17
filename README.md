# The official Todoist Python API library

Welcome to the official client to the [Todoist Sync API](https://developer.todoist.com/sync/).

This client makes actions using the Sync API easier to use and also caches
values locally to make right usage of the partial sync mechanism of the API.

## Installing

The package can be installed as any other pip package:

```bash
pip install todoist-python
```

The official Documentation can be found at
https://todoist-python.readthedocs.io/en/latest/.

## Using

You can import `todoist-python` on your Python application or just try it out
from the python REPL (read-eval-print-loop).

This is how it looks like when using the REPL:


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

The `state` attribute has all the data of your full sync and the `sync` method
does the job of keeping things in sync in the best way possible.

You can add or change data as well. Let's add a task and change it as examples:


```python
$ python
>>> import todoist
>>> api = todoist.TodoistAPI('0123456789abcdef0123456789abcdef01234567')
>>> item = api.items.add('My taks')  # oh no, typo!
>>> api.commit()  # commit the changes to the server
{'id': 1234567890, u'content': u'My taks', u'user_id': 1, ...}
>>>
>>> api.items.update(item['id'], content='My task')
>>> api.commit()  # never forget to commit!
{'id': 1234567890, u'content': u'My task', u'user_id': 1, ...}
```

That's it! To know what actions are available for each object, refer to
`Managers` in our [official documentation](https://todoist-python.readthedocs.io).

We also document all the actions available on this library along with our
official API documentation. Here is one example of the [add task
endpoint](https://developer.todoist.com/sync/v8/?python#add-an-item). Check the
_python_ tab on the examples for actions related to this library.


## Development

### Build Project

This project still supports Python 2.7 but **we recommend Python 3**.

We recommend using [virtualenv](https://pypi.python.org/pypi/virtualenv) and
[pip](https://pypi.python.org/pypi/pip) for the project bootstrap. Below is a
step by step of the bootstrap process:

Clone the repo and enter it:

    $ git clone git@github.com:Doist/todoist-python.git ; cd todoist-python

Create an environment:

    $ virtualenv --system-site-packages -p /usr/bin/python2.7 env # if you need python2.7
    $ virtualenv --system-site-packages env # use only python3 if you run this

Activate the environment:

    $ source env/bin/activate

Install the library along with all the dependencies (just `requests` for this project):

    $ pip install -e .


### Build Documentation

If you want to build the documentation as well, install some extra packages:

    $ pip install -r doc/requirements.txt

Build the documentation:

    $ (cd doc ; make html)

Read the built documentation by opening:

    doc/_build/html/index.html

## Testing the library

We have a set of tests to ensure we support Python both 2.x and 3.x.

To test it out, please make sure you have python 2 and python 3 installed in
your system. Then install "tox" either globally (preferred way) or in your local
environment.

    # apt-get install python-tox

or

    $ pip install tox


You will also need to have the `pytest.ini` file. We are providing a
`pytest.ini.sample` that you can copy and paste to create your own
`pytest.ini`.

You will need two different tokens (`token` and `token2` keys on on
`pytest.ini`) to be able to run all the tests successfully, since we have tests
for the sharing features.

With the setup done, you can just run:

    $ tox

Keep in mind that running the whole test suit may cause some tests to fail as
you will certaily hit some limits of API usage. We recommend only running the
test for your feature.
