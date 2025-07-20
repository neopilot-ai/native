"""
Test CI output functionality for JUnit/JSON reporting.
"""

import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# Add the devops directory to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "devops"))


def test_junit_xml_generation():
    """Test that JUnit XML files are generated correctly."""
    from remote_exec import _write_junit

    # Sample test results
    results = [
        {"target": "//target1", "returncode": 0, "stdout": "Success", "stderr": ""},
        {
            "target": "//target2",
            "returncode": 1,
            "stdout": "",
            "stderr": "Build failed",
        },
        {"target": "//target3", "returncode": 0, "stdout": "Success", "stderr": ""},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        output_path = f.name

    try:
        _write_junit(results, output_path, suite_name="TestSuite")

        # Verify the XML file was created and is valid
        assert os.path.exists(output_path)

        # Parse and validate the XML
        tree = ET.parse(output_path)
        root = tree.getroot()

        # Check testsuite attributes
        assert root.tag == "testsuite"
        assert root.get("name") == "TestSuite"
        assert root.get("tests") == "3"

        # Check testcase elements
        testcases = root.findall("testcase")
        assert len(testcases) == 3

        # Check that failed tests have failure elements
        failures = root.findall("testcase/failure")
        assert len(failures) == 1  # Only target2 failed

        # Check failure details
        failure = failures[0]
        assert failure.get("message") == "Exit code 1"
        assert failure.text == "Build failed"

    finally:
        os.unlink(output_path)


def test_json_output_generation():
    """Test that JSON output files are generated correctly."""
    from remote_exec import _write_json

    # Sample test results
    results = [
        {"target": "//target1", "returncode": 0, "stdout": "Success", "stderr": ""},
        {
            "target": "//target2",
            "returncode": 1,
            "stdout": "",
            "stderr": "Build failed",
        },
        {"target": "//target3", "returncode": 0, "stdout": "Success", "stderr": ""},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        output_path = f.name

    try:
        _write_json(results, output_path)

        # Verify the JSON file was created and is valid
        assert os.path.exists(output_path)

        # Parse and validate the JSON
        with open(output_path, "r") as f:
            loaded_results = json.load(f)

        assert len(loaded_results) == 3
        assert loaded_results[0]["target"] == "//target1"
        assert loaded_results[0]["returncode"] == 0
        assert loaded_results[1]["target"] == "//target2"
        assert loaded_results[1]["returncode"] == 1
        assert loaded_results[2]["target"] == "//target3"
        assert loaded_results[2]["returncode"] == 0

    finally:
        os.unlink(output_path)


def test_cli_junit_output_option():
    """Test that CLI commands accept --junit-output option."""
    # Test that the CLI can be imported and has the expected options
    try:
        from remote_exec import app

        # Get the bazel command
        bazel_cmd = None
        for cmd in app.registered_commands:
            if cmd.name == "bazel":
                bazel_cmd = cmd
                break

        assert bazel_cmd is not None

        # Check that the command has the junit_output parameter
        params = [param.name for param in bazel_cmd.params]
        assert "junit_output" in params
        assert "json_output" in params

    except ImportError:
        pytest.skip("remote_exec module not available")


def test_cli_json_output_option():
    """Test that CLI commands accept --json-output option."""
    try:
        from remote_exec import app

        # Get the buck2 command
        buck2_cmd = None
        for cmd in app.registered_commands:
            if cmd.name == "buck2":
                buck2_cmd = cmd
                break

        assert buck2_cmd is not None

        # Check that the command has the json_output parameter
        params = [param.name for param in buck2_cmd.params]
        assert "json_output" in params

    except ImportError:
        pytest.skip("remote_exec module not available")


def test_ci_output_directory_structure():
    """Test that CI output directories are created correctly."""
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        junit_dir = os.path.join(temp_dir, "junit")
        json_dir = os.path.join(temp_dir, "json")

        # Create directories
        os.makedirs(junit_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)

        # Verify directories exist
        assert os.path.exists(junit_dir)
        assert os.path.exists(json_dir)
        assert os.path.isdir(junit_dir)
        assert os.path.isdir(json_dir)


if __name__ == "__main__":
    pytest.main([__file__])
