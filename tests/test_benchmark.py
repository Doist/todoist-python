import test_api


def test_benchmark_project(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_project, cleanup, api_endpoint, api_token)


def test_benchmark_item(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_item, cleanup, api_endpoint, api_token)


def test_benchmark_label(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_label, cleanup, api_endpoint, api_token)


def test_benchmark_note(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_note, cleanup, api_endpoint, api_token)


def test_benchmark_projectnote(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_projectnote, cleanup, api_endpoint, api_token)


def test_benchmark_filter(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_filter, cleanup, api_endpoint, api_token)


def test_benchmark_reminder(cleanup, api_endpoint, api_token, benchmark):
    benchmark(test_api.test_reminder, cleanup, api_endpoint, api_token)


def test_benchmark_share(cleanup, api_endpoint, api_token, api_token2, benchmark):
    benchmark(test_api.test_share, cleanup, api_endpoint, api_token, api_token2)
