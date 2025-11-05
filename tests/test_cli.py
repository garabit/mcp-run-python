from __future__ import annotations as _annotations

import os
from unittest.mock import patch

import pytest

from mcp_run_python._cli import cli_logic
from mcp_run_python.main import _deno_run_args


def test_cli_version(capsys: pytest.CaptureFixture[str]):
    assert cli_logic(['--version']) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith('mcp-run-python ')


def test_cli_example_success():
    assert cli_logic(['--deps', 'numpy', 'example']) == 0


def test_cli_example_fail():
    assert cli_logic(['example']) == 1


def test_deno_run_args_with_host():
    """Test that --host flag is passed to deno args when specified."""
    args = _deno_run_args(
        'streamable_http',
        http_port=9000,
        http_host='0.0.0.0',
    )
    assert '--host=0.0.0.0' in args
    assert '--port=9000' in args


def test_deno_run_args_default_host():
    """Test that default host (127.0.0.1) doesn't add --host flag."""
    args = _deno_run_args(
        'streamable_http',
        http_port=9000,
        http_host='127.0.0.1',
    )
    assert '--host=127.0.0.1' not in args
    assert '--port=9000' in args


def test_deno_run_args_host_requires_streamable_http():
    """Test that --host flag raises error for non-streamable_http modes."""
    with pytest.raises(ValueError, match='Host is only supported for `streamable_http` mode'):
        _deno_run_args(
            'stdio',
            http_host='0.0.0.0',
        )


def test_cli_host_env_var():
    """Test that HOST environment variable is used when --host not specified."""
    with patch.dict(os.environ, {'HOST': '192.168.1.1'}):
        with patch('mcp_run_python._cli.run_mcp_server') as mock_run:
            mock_run.return_value = 0
            cli_logic(['--port', '9000', 'streamable-http'])
            mock_run.assert_called_once()
            assert mock_run.call_args[1]['http_host'] == '192.168.1.1'


def test_cli_host_flag_overrides_env():
    """Test that --host flag overrides HOST environment variable."""
    with patch.dict(os.environ, {'HOST': '192.168.1.1'}):
        with patch('mcp_run_python._cli.run_mcp_server') as mock_run:
            mock_run.return_value = 0
            cli_logic(['--port', '9000', '--host', '0.0.0.0', 'streamable-http'])
            mock_run.assert_called_once()
            assert mock_run.call_args[1]['http_host'] == '0.0.0.0'
