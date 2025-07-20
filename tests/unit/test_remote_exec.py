import sys
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

sys.path.append("devops")
import remote_exec

runner = CliRunner()


# Helper to mock subprocess.run
class MockCompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@patch("shutil.which", return_value="/usr/bin/bazel")
@patch(
    "subprocess.run",
    return_value=MockCompletedProcess(stdout="Bazel build success", stderr=""),
)
def test_bazel_success(mock_run, mock_which):
    result = runner.invoke(remote_exec.app, ["bazel", "build", "//my:target"])
    assert "Bazel build success" in result.output
    assert result.exit_code == 0


@patch("shutil.which", return_value=None)
def test_bazel_not_found(mock_which):
    result = runner.invoke(remote_exec.app, ["bazel", "build", "//my:target"])
    assert "Error: 'bazel' not found in PATH" in result.output
    assert result.exit_code == 1


@patch("shutil.which", return_value="/usr/bin/buck2")
@patch(
    "subprocess.run",
    return_value=MockCompletedProcess(stdout="Buck2 build success", stderr=""),
)
def test_buck2_success(mock_run, mock_which):
    result = runner.invoke(remote_exec.app, ["buck2", "build", "//my:target"])
    assert "Buck2 build success" in result.output
    assert result.exit_code == 0


@patch("shutil.which", return_value=None)
def test_buck2_not_found(mock_which):
    result = runner.invoke(remote_exec.app, ["buck2", "build", "//my:target"])
    assert "Error: 'buck2' not found in PATH" in result.output
    assert result.exit_code == 1


@patch("shutil.which", side_effect=[None, "/usr/bin/gomacc"])
@patch(
    "subprocess.run",
    return_value=MockCompletedProcess(stdout="Goma build success", stderr=""),
)
def test_goma_success(mock_run, mock_which):
    result = runner.invoke(remote_exec.app, ["goma", "build", "//my:target"])
    assert "Goma build success" in result.output
    assert result.exit_code == 0


@patch("shutil.which", side_effect=[None, None])
def test_goma_not_found(mock_which):
    result = runner.invoke(remote_exec.app, ["goma", "build", "//my:target"])
    assert "Error: 'goma' or 'gomacc' not found in PATH" in result.output
    assert result.exit_code == 1


@patch("shutil.which", side_effect=[None, "/usr/bin/reproxy"])
@patch(
    "subprocess.run",
    return_value=MockCompletedProcess(stdout="Reclient build success", stderr=""),
)
def test_reclient_success(mock_run, mock_which):
    result = runner.invoke(remote_exec.app, ["reclient", "build", "//my:target"])
    assert "Reclient build success" in result.output
    assert result.exit_code == 0


@patch("shutil.which", side_effect=[None, None])
def test_reclient_not_found(mock_which):
    result = runner.invoke(remote_exec.app, ["reclient", "build", "//my:target"])
    assert "Error: 'reclient' or 'reproxy' not found in PATH" in result.output
    assert result.exit_code == 1


if __name__ == "__main__":
    pytest.main([__file__])
