#!/usr/bin/env python3
"""
Demonstration of JUnit/JSON output functionality for CI dashboards.
This script shows how the remote execution CLI generates test result files.
"""

import json
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def write_junit(results, output_path, suite_name="BuildResults"):
    """Write JUnit XML format test results."""
    testsuite = ET.Element("testsuite", name=suite_name, tests=str(len(results)))
    for r in results:
        testcase = ET.SubElement(
            testsuite, "testcase", name=r["target"], classname=suite_name
        )
        if r["returncode"] != 0:
            failure = ET.SubElement(
                testcase, "failure", message=f"Exit code {r['returncode']}"
            )
            failure.text = r["stderr"] or r["stdout"]
    tree = ET.ElementTree(testsuite)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def write_json(results, output_path):
    """Write JSON format test results."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def main():
    """Demonstrate JUnit/JSON output functionality."""
    print("🔧 CI Dashboard Output Demonstration")
    print("=" * 50)

    # Sample build/test results
    results = [
        {
            "target": "//core:memory_store",
            "returncode": 0,
            "stdout": "Build successful",
            "stderr": "",
        },
        {
            "target": "//core:token_forge",
            "returncode": 1,
            "stdout": "",
            "stderr": "Compilation failed: missing dependency",
        },
        {
            "target": "//tests:unit_tests",
            "returncode": 0,
            "stdout": "All tests passed",
            "stderr": "",
        },
        {
            "target": "//apps:cli",
            "returncode": 2,
            "stdout": "",
            "stderr": "Runtime error: configuration file not found",
        },
    ]

    # Create output directory
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)

    # Generate JUnit XML
    junit_path = output_dir / "demo-build.xml"
    write_junit(results, junit_path, suite_name="DemoBuild")
    print(f"✅ Generated JUnit XML: {junit_path}")

    # Generate JSON
    json_path = output_dir / "demo-build.json"
    write_json(results, json_path)
    print(f"✅ Generated JSON: {json_path}")

    # Show JUnit XML content
    print("\n📄 JUnit XML Content:")
    print("-" * 30)
    with open(junit_path, "r") as f:
        print(f.read())

    # Show JSON content
    print("\n📄 JSON Content:")
    print("-" * 30)
    with open(json_path, "r") as f:
        print(json.dumps(json.load(f), indent=2))

    # Show summary
    print("\n📊 Build Summary:")
    print("-" * 30)
    success_count = sum(1 for r in results if r["returncode"] == 0)
    failure_count = len(results) - success_count

    print(f"Total targets: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Success rate: {success_count/len(results)*100:.1f}%")

    # Show failed targets
    if failure_count > 0:
        print("\n❌ Failed targets:")
        for r in results:
            if r["returncode"] != 0:
                print(f"  - {r['target']} (exit code: {r['returncode']})")
                if r["stderr"]:
                    print(f"    Error: {r['stderr']}")

    print(f"\n🎯 CI Integration:")
    print(f"  - JUnit XML files can be uploaded to GitHub Actions, Jenkins, etc.")
    print(f"  - JSON files can be used for custom dashboards or further processing")
    print(f"  - Both formats include target names, exit codes, and error messages")

    print(f"\n📁 Files created in: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
