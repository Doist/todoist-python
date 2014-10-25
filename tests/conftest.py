import pytest


def pytest_addoption(parser):
    parser.addoption('--email', help='Set up the user email')
    parser.addini('email', help='Set up the user email')
    parser.addoption('--password', help='Set up the user password')
    parser.addini('password', help='Set up the user password')
    parser.addoption('--token', help='Set up the API token')
    parser.addini('token', help='Set up the API token')
    parser.addoption('--email2', help='Set up another user email')
    parser.addini('email2', help='Set up another user email')
    parser.addoption('--password2', help='Set up another user password')
    parser.addini('password2', help='Set up another user password')
    parser.addoption('--token2', help='Set up another API token')
    parser.addini('token2', help='Set up another API token')


@pytest.fixture
def user_email(request):
    email = request.config.getini('email')
    if not email:
        email = request.config.getoption('--email')
    if not email:
        raise RuntimeError('User email not defined. Please use the '
                           '--email commandline option, or the "token" '
                           'attribute in your pytest.ini')
    return email


@pytest.fixture
def user_password(request):
    password = request.config.getini('password')
    if not password:
        password = request.config.getoption('--password')
    if not password:
        raise RuntimeError('User password not defined. Please use the '
                           '--password commandline option, or the "token" '
                           'attribute in your pytest.ini')
    return password


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
def user_email2(request):
    email2 = request.config.getini('email2')
    if not email2:
        email2 = request.config.getoption('--email2')
    if not email2:
        raise RuntimeError('User email2 not defined. Please use the '
                           '--email2 commandline option, or the "token" '
                           'attribute in your pytest.ini')
    return email2


@pytest.fixture
def user_password2(request):
    password2 = request.config.getini('password2')
    if not password2:
        password2 = request.config.getoption('--password2')
    if not password2:
        raise RuntimeError('User password2 not defined. Please use the '
                           '--password2 commandline option, or the "token" '
                           'attribute in your pytest.ini')
    return password2


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


