import pytest

import todoist


def pytest_addoption(parser):
    parser.addoption('--endpoint', help='Set up the test endpoint')
    parser.addini('endpoint', help='Set up the test endpoint')
    parser.addoption('--token', help='Set up the API token')
    parser.addini('token', help='Set up the API token')
    parser.addoption('--token2', help='Set up another API token')
    parser.addini('token2', help='Set up another API token')


@pytest.fixture
def api_endpoint(request):
    endpoint = request.config.getini('endpoint')
    if not endpoint:
        endpoint = request.config.getoption('--endpoint')
    if not endpoint:
        raise RuntimeError('Test endpoint not defined. Please use the '
                           '--endpoint commandline option, or the "endpoint" '
                           'attribute in your pytest.ini')
    return endpoint


@pytest.fixture
def api_token(request):
    token = request.config.getini('token')
    if not token:
        token = request.config.getoption('--token')
    if not token:
        raise RuntimeError('API token not defined. Please use the --token '
                           'commandline option, or the "token" attribute in '
                           'your pytest.ini')
    return token


@pytest.fixture
def api_token2(request):
    token2 = request.config.getini('token2')
    if not token2:
        token2 = request.config.getoption('--token2')
    if not token2:
        raise RuntimeError('API token2 not defined. Please use the --token2 '
                           'commandline option, or the "token2" attribute in '
                           'your pytest.ini')
    return token2


@pytest.fixture
def cleanup(api_endpoint, api_token):
    _cleanup(api_endpoint, api_token)


@pytest.fixture
def cleanup2(api_endpoint, api_token2):
    _cleanup(api_endpoint, api_token2)


def _cleanup(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()
    for filter in api.state['filters'][:]:
        filter.delete()
    api.commit()
    for label in api.state['labels'][:]:
        label.delete()
    api.commit()
    for reminder in api.state['reminders'][:]:
        reminder.delete()
    api.commit()
    for note in api.state['notes'][:]:
        note.delete()
    api.commit()
    for note in api.state['project_notes'][:]:
        note.delete()
    api.commit()
    for item in api.state['items'][:]:
        item.delete()
    api.commit()
    for section in api.state['sections'][:]:
        section.delete()
    api.commit()
    for project in api.state['projects'][:]:
        if project['name'] != 'Inbox':
            project.delete()
    api.commit()
