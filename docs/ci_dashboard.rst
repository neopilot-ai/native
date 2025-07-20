CI Dashboard Integration
========================

The AI Native Systems project includes comprehensive CI Dashboard integration with JUnit XML and JSON output support for build and test results. This enables seamless integration with CI/CD platforms and custom dashboards.

Overview
--------

The CI Dashboard integration provides:

* **JUnit XML Output**: Standard format for CI platforms (GitHub Actions, Jenkins, GitLab CI, etc.)
* **JSON Output**: Machine-readable format for custom dashboards and analytics
* **CLI Integration**: All remote execution commands support output generation
* **CI Workflow Integration**: Automated test result generation and artifact upload
* **Makefile Targets**: Convenient shortcuts for CI output generation

Remote Execution CLI
-------------------

All remote execution commands support JUnit and JSON output generation:

Bazel Integration
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Generate JUnit XML only
    poetry run python devops/remote_exec.py bazel build //... --junit-output=test-results/bazel-build.xml

    # Generate JSON only
    poetry run python devops/remote_exec.py bazel build //... --json-output=test-results/bazel-build.json

    # Generate both formats
    poetry run python devops/remote_exec.py bazel build //... \
        --junit-output=test-results/bazel-build.xml \
        --json-output=test-results/bazel-build.json

    # With remote execution
    poetry run python devops/remote_exec.py bazel build //... --remote \
        --junit-output=test-results/bazel-remote-build.xml \
        --json-output=test-results/bazel-remote-build.json

Buck2 Integration
~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Generate both formats for Buck2
    poetry run python devops/remote_exec.py buck2 build //... \
        --junit-output=test-results/buck2-build.xml \
        --json-output=test-results/buck2-build.json

    # Test execution with output
    poetry run python devops/remote_exec.py buck2 test //... \
        --junit-output=test-results/buck2-tests.xml \
        --json-output=test-results/buck2-tests.json

Goma Integration
~~~~~~~~~~~~~~~

.. code-block:: bash

    # Generate both formats for Goma
    poetry run python devops/remote_exec.py goma build //... \
        --junit-output=test-results/goma-build.xml \
        --json-output=test-results/goma-build.json

Reclient Integration
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Generate both formats for Reclient
    poetry run python devops/remote_exec.py reclient build //... \
        --junit-output=test-results/reclient-build.xml \
        --json-output=test-results/reclient-build.json

Makefile Integration
-------------------

The project includes convenient Makefile targets for CI output generation:

.. code-block:: bash

    # Demonstrate CI output functionality
    make demo-ci-output

    # Generate CI output for each build system
    make bazel-ci      # Creates bazel-build.xml + bazel-build.json
    make buck2-ci      # Creates buck2-build.xml + buck2-build.json
    make goma-ci       # Creates goma-build.xml + goma-build.json
    make reclient-ci   # Creates reclient-build.xml + reclient-build.json

    # Run CI output tests
    make test-ci-output

Output Formats
-------------

JUnit XML Format
~~~~~~~~~~~~~~~

JUnit XML is the standard format for CI platforms. Each build target becomes a test case:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <testsuite name="BazelBuild" tests="3">
        <testcase name="//core:memory_store" classname="BazelBuild"/>
        <testcase name="//core:token_forge" classname="BazelBuild">
            <failure message="Exit code 1">Compilation failed: missing dependency</failure>
        </testcase>
        <testcase name="//tests:unit_tests" classname="BazelBuild"/>
    </testsuite>

JSON Format
~~~~~~~~~~

JSON format provides machine-readable data for custom dashboards and analytics:

.. code-block:: json

    [
        {
            "target": "//core:memory_store",
            "returncode": 0,
            "stdout": "Build successful",
            "stderr": ""
        },
        {
            "target": "//core:token_forge",
            "returncode": 1,
            "stdout": "",
            "stderr": "Compilation failed: missing dependency"
        },
        {
            "target": "//tests:unit_tests",
            "returncode": 0,
            "stdout": "All tests passed",
            "stderr": ""
        }
    ]

CI Workflow Integration
----------------------

GitHub Actions Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:

1. **Generates test results** with JUnit XML and JSON output
2. **Uploads artifacts** for CI dashboards:
   * ``ci-dashboard-results``: Complete test results and summaries
   * ``junit-test-results``: JUnit XML files for GitHub Actions test reporting
3. **Publishes test results** to GitHub using the ``publish-unit-test-result-action``

Example workflow output:

.. code-block:: yaml

    - name: Run remote build/test CLI (Bazel example) with JUnit/JSON output
      run: |
        poetry run python devops/remote_exec.py bazel build //... \
            --junit-output=test-results/junit/bazel-build.xml \
            --json-output=test-results/json/bazel-build.json || true

    - name: Upload test results and CI dashboard artifacts
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: ci-dashboard-results
        path: |
          test-results/
          demo_results/
        if-no-files-found: ignore

    - name: Publish test results to GitHub
      if: always()
      uses: EnricoMi/publish-unit-test-result-action@v2
      with:
        files: "test-results/junit/*.xml"

Custom Dashboard Integration
---------------------------

Python Integration
~~~~~~~~~~~~~~~~~

Process JSON results for custom dashboards:

.. code-block:: python

    import json
    from pathlib import Path

    def analyze_build_results(json_path):
        """Analyze build results from JSON output."""
        with open(json_path, 'r') as f:
            results = json.load(f)
        
        total_targets = len(results)
        successful = sum(1 for r in results if r['returncode'] == 0)
        failed = total_targets - successful
        success_rate = successful / total_targets * 100
        
        return {
            'total_targets': total_targets,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'failed_targets': [r['target'] for r in results if r['returncode'] != 0]
        }

    # Usage
    results = analyze_build_results('test-results/bazel-build.json')
    print(f"Build Success Rate: {results['success_rate']:.1f}%")

JUnit XML Processing
~~~~~~~~~~~~~~~~~~~

Process JUnit XML results:

.. code-block:: python

    import xml.etree.ElementTree as ET

    def analyze_junit_results(xml_path):
        """Analyze JUnit XML results."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        total_tests = int(root.get('tests'))
        failures = len(root.findall('testcase/failure'))
        success_rate = (total_tests - failures) / total_tests * 100
        
        return {
            'total_tests': total_tests,
            'failures': failures,
            'success_rate': success_rate
        }

    # Usage
    results = analyze_junit_results('test-results/bazel-build.xml')
    print(f"Test Success Rate: {results['success_rate']:.1f}%")

JavaScript Integration
~~~~~~~~~~~~~~~~~~~~~

Process results in web dashboards:

.. code-block:: javascript

    async function loadBuildResults() {
        const response = await fetch('test-results/bazel-build.json');
        const results = await response.json();
        
        const successful = results.filter(r => r.returncode === 0).length;
        const failed = results.length - successful;
        const successRate = (successful / results.length) * 100;
        
        // Update dashboard
        document.getElementById('success-rate').textContent = `${successRate.toFixed(1)}%`;
        document.getElementById('total-targets').textContent = results.length;
        document.getElementById('failed-targets').textContent = failed;
    }

Usage Examples
-------------

Basic Usage
~~~~~~~~~~

Generate output for a single build:

.. code-block:: bash

    # Create output directories
    mkdir -p test-results/junit test-results/json

    # Run build with output generation
    poetry run python devops/remote_exec.py bazel build //my:target \
        --junit-output=test-results/junit/bazel-build.xml \
        --json-output=test-results/json/bazel-build.json

Batch Processing
~~~~~~~~~~~~~~~

Process multiple targets with parallel execution:

.. code-block:: bash

    # Create targets file
    echo "//core:memory_store" > targets.txt
    echo "//core:token_forge" >> targets.txt
    echo "//tests:unit_tests" >> targets.txt

    # Run with targets file and output generation
    poetry run python devops/remote_exec.py bazel build //... \
        --targets-file=targets.txt \
        --max-workers=4 \
        --junit-output=test-results/junit/bazel-batch.xml \
        --json-output=test-results/json/bazel-batch.json

CI Pipeline Integration
~~~~~~~~~~~~~~~~~~~~~~

Integrate into CI/CD pipelines:

.. code-block:: yaml

    # Example: GitLab CI
    build_and_test:
        stage: test
        script:
            - mkdir -p test-results/junit test-results/json
            - poetry run python devops/remote_exec.py bazel build //... \
                --junit-output=test-results/junit/bazel-build.xml \
                --json-output=test-results/json/bazel-build.json
        artifacts:
            reports:
                junit: test-results/junit/*.xml
            paths:
                - test-results/

Testing
-------

Run tests for CI output functionality:

.. code-block:: bash

    # Run CI output tests
    make test-ci-output

    # Or directly with pytest
    PYTHONPATH=. python3 -m pytest tests/unit/test_ci_output.py -v

Demonstration
------------

Run the demonstration script to see the functionality in action:

.. code-block:: bash

    make demo-ci-output

This will generate sample JUnit XML and JSON files and display their contents.

Configuration
-------------

Output Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

The recommended output directory structure:

.. code-block:: text

    test-results/
    ├── junit/
    │   ├── bazel-build.xml
    │   ├── buck2-build.xml
    │   ├── goma-build.xml
    │   └── reclient-build.xml
    └── json/
        ├── bazel-build.json
        ├── buck2-build.json
        ├── goma-build.json
        └── reclient-build.json

File Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~

Recommended naming conventions:

* **JUnit XML**: ``{build-system}-{command}.xml`` (e.g., ``bazel-build.xml``, ``buck2-test.xml``)
* **JSON**: ``{build-system}-{command}.json`` (e.g., ``bazel-build.json``, ``buck2-test.json``)

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Missing dependencies:**
.. code-block:: bash

    # Install required dependencies
    poetry install --with dev

**Permission errors:**
.. code-block:: bash

    # Ensure output directories are writable
    mkdir -p test-results/junit test-results/json
    chmod 755 test-results/

**Invalid XML/JSON:**
.. code-block:: bash

    # Validate generated files
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('test-results/junit/bazel-build.xml')"
    python3 -c "import json; json.load(open('test-results/json/bazel-build.json'))"

Best Practices
-------------

1. **Always use both formats** for maximum compatibility
2. **Organize output files** in structured directories
3. **Include error handling** in custom dashboard code
4. **Validate output files** before processing
5. **Use consistent naming** conventions across projects
6. **Archive historical results** for trend analysis

API Reference
-------------

CLI Options
~~~~~~~~~~

All remote execution commands support these options:

* ``--junit-output PATH``: Write JUnit XML summary to specified file
* ``--json-output PATH``: Write JSON summary to specified file
* ``--max-workers N``: Maximum parallel builds/tests (default: 4)
* ``--targets TARGETS``: Comma-separated list of targets
* ``--targets-file FILE``: File with one target per line
* ``--extra ARGS``: Extra build system arguments

Output Schema
~~~~~~~~~~~~

JSON output schema:

.. code-block:: json

    [
        {
            "target": "string",      // Build target identifier
            "returncode": "integer", // Exit code (0 = success)
            "stdout": "string",      // Standard output
            "stderr": "string"       // Standard error
        }
    ]

JUnit XML schema follows the standard JUnit format with:
* ``testsuite``: Root element with test count
* ``testcase``: Individual test cases (one per target)
* ``failure``: Failure details for failed targets 