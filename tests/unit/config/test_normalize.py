import pytest

from borgmatic.config import normalize as module


@pytest.mark.parametrize(
    'config,expected_config,produces_logs',
    (
        (
            {'location': {'exclude_if_present': '.nobackup'}},
            {'location': {'exclude_if_present': ['.nobackup']}},
            True,
        ),
        (
            {'location': {'exclude_if_present': ['.nobackup']}},
            {'location': {'exclude_if_present': ['.nobackup']}},
            False,
        ),
        (
            {'location': {'source_directories': ['foo', 'bar']}},
            {'location': {'source_directories': ['foo', 'bar']}},
            False,
        ),
        (
            {'location': None},
            {'location': None},
            False,
        ),
        (
            {'storage': {'compression': 'yes_please'}},
            {'storage': {'compression': 'yes_please'}},
            False,
        ),
        (
            {'storage': None},
            {'storage': None},
            False,
        ),
        (
            {'hooks': {'healthchecks': 'https://example.com'}},
            {'hooks': {'healthchecks': {'ping_url': 'https://example.com'}}},
            True,
        ),
        (
            {'hooks': {'cronitor': 'https://example.com'}},
            {'hooks': {'cronitor': {'ping_url': 'https://example.com'}}},
            True,
        ),
        (
            {'hooks': {'pagerduty': 'https://example.com'}},
            {'hooks': {'pagerduty': {'integration_key': 'https://example.com'}}},
            True,
        ),
        (
            {'hooks': {'cronhub': 'https://example.com'}},
            {'hooks': {'cronhub': {'ping_url': 'https://example.com'}}},
            True,
        ),
        (
            {'hooks': None},
            {'hooks': None},
            False,
        ),
        (
            {'consistency': {'checks': ['archives']}},
            {'consistency': {'checks': [{'name': 'archives'}]}},
            True,
        ),
        (
            {'consistency': {'checks': ['archives']}},
            {'consistency': {'checks': [{'name': 'archives'}]}},
            True,
        ),
        (
            {'consistency': None},
            {'consistency': None},
            False,
        ),
        (
            {'location': {'numeric_owner': False}},
            {'location': {'numeric_ids': False}},
            True,
        ),
        (
            {'location': {'bsd_flags': False}},
            {'location': {'flags': False}},
            True,
        ),
        (
            {'storage': {'remote_rate_limit': False}},
            {'storage': {'upload_rate_limit': False}},
            True,
        ),
        (
            {'location': {'repositories': ['foo@bar:/repo']}},
            {'location': {'repositories': [{'path': 'ssh://foo@bar/repo'}]}},
            True,
        ),
        (
            {'location': {'repositories': ['foo@bar:repo']}},
            {'location': {'repositories': [{'path': 'ssh://foo@bar/./repo'}]}},
            True,
        ),
        (
            {'location': {'repositories': ['foo@bar:~/repo']}},
            {'location': {'repositories': [{'path': 'ssh://foo@bar/~/repo'}]}},
            True,
        ),
        (
            {'location': {'repositories': ['ssh://foo@bar:1234/repo']}},
            {'location': {'repositories': [{'path': 'ssh://foo@bar:1234/repo'}]}},
            True,
        ),
        (
            {'location': {'repositories': ['file:///repo']}},
            {'location': {'repositories': [{'path': '/repo'}]}},
            True,
        ),
        (
            {'location': {'repositories': [{'path': 'foo@bar:/repo', 'label': 'foo'}]}},
            {'location': {'repositories': [{'path': 'ssh://foo@bar/repo', 'label': 'foo'}]}},
            True,
        ),
        (
            {'location': {'repositories': [{'path': 'file:///repo', 'label': 'foo'}]}},
            {'location': {'repositories': [{'path': '/repo', 'label': 'foo'}]}},
            False,
        ),
        (
            {'location': {'repositories': [{'path': '/repo', 'label': 'foo'}]}},
            {'location': {'repositories': [{'path': '/repo', 'label': 'foo'}]}},
            False,
        ),
        (
            {'consistency': {'prefix': 'foo'}},
            {'consistency': {'prefix': 'foo'}},
            True,
        ),
        (
            {'retention': {'prefix': 'foo'}},
            {'retention': {'prefix': 'foo'}},
            True,
        ),
    ),
)
def test_normalize_applies_hard_coded_normalization_to_config(
    config, expected_config, produces_logs
):
    logs = module.normalize('test.yaml', config)

    assert config == expected_config

    if produces_logs:
        assert logs
    else:
        assert logs == []


def test_normalize_raises_error_if_repository_data_is_not_consistent():
    with pytest.raises(TypeError):
        module.normalize(
            'test.yaml',
            {
                'location': {
                    'repositories': [{'path': 'foo@bar:/repo', 'label': 'foo'}, 'file:///repo']
                }
            },
        )
