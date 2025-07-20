CI Dashboard Quick Reference
============================

Quick reference for CI Dashboard integration with JUnit/JSON output.

CLI Commands
-----------

Basic Usage
~~~~~~~~~~

.. code-block:: bash

    # Generate JUnit XML only
    poetry run python devops/remote_exec.py bazel build //... --junit-output=results.xml

    # Generate JSON only
    poetry run python devops/remote_exec.py buck2 test //... --json-output=results.json

    # Generate both formats
    poetry run python devops/remote_exec.py goma build //... \
        --junit-output=results.xml --json-output=results.json

Makefile Shortcuts
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    make demo-ci-output    # Demonstrate functionality
    make bazel-ci         # Bazel with CI output
    make buck2-ci         # Buck2 with CI output
    make goma-ci          # Goma with CI output
    make reclient-ci      # Reclient with CI output
    make test-ci-output   # Run CI output tests

Build Systems
------------

Bazel
~~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py bazel build //... \
        --junit-output=test-results/bazel-build.xml \
        --json-output=test-results/bazel-build.json

    poetry run python devops/remote_exec.py bazel test //... \
        --junit-output=test-results/bazel-tests.xml \
        --json-output=test-results/bazel-tests.json

Buck2
~~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py buck2 build //... \
        --junit-output=test-results/buck2-build.xml \
        --json-output=test-results/buck2-build.json

    poetry run python devops/remote_exec.py buck2 test //... \
        --junit-output=test-results/buck2-tests.xml \
        --json-output=test-results/buck2-tests.json

Goma
~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py goma build //... \
        --junit-output=test-results/goma-build.xml \
        --json-output=test-results/goma-build.json

Reclient
~~~~~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py reclient build //... \
        --junit-output=test-results/reclient-build.xml \
        --json-output=test-results/reclient-build.json

Advanced Options
---------------

Parallel Execution
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py bazel build //... \
        --max-workers=8 \
        --junit-output=test-results/bazel-parallel.xml \
        --json-output=test-results/bazel-parallel.json

Target Selection
~~~~~~~~~~~~~~~

.. code-block:: bash

    # Specific targets
    poetry run python devops/remote_exec.py bazel build //core:memory_store //core:token_forge \
        --junit-output=test-results/bazel-specific.xml \
        --json-output=test-results/bazel-specific.json

    # Targets from file
    poetry run python devops/remote_exec.py bazel build //... \
        --targets-file=targets.txt \
        --junit-output=test-results/bazel-file.xml \
        --json-output=test-results/bazel-file.json

Remote Execution
~~~~~~~~~~~~~~~

.. code-block:: bash

    poetry run python devops/remote_exec.py bazel build //... --remote \
        --junit-output=test-results/bazel-remote.xml \
        --json-output=test-results/bazel-remote.json

Output Formats
-------------

JUnit XML Structure
~~~~~~~~~~~~~~~~~~

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <testsuite name="BazelBuild" tests="3">
        <testcase name="//target1" classname="BazelBuild"/>
        <testcase name="//target2" classname="BazelBuild">
            <failure message="Exit code 1">Build failed</failure>
        </testcase>
        <testcase name="//target3" classname="BazelBuild"/>
    </testsuite>

JSON Structure
~~~~~~~~~~~~~

.. code-block:: json

    [
        {
            "target": "//target1",
            "returncode": 0,
            "stdout": "Success",
            "stderr": ""
        },
        {
            "target": "//target2",
            "returncode": 1,
            "stdout": "",
            "stderr": "Build failed"
        }
    ]

CI Integration
-------------

GitHub Actions
~~~~~~~~~~~~~

.. code-block:: yaml

    - name: Run build with CI output
      run: |
        mkdir -p test-results/junit test-results/json
        poetry run python devops/remote_exec.py bazel build //... \
            --junit-output=test-results/junit/bazel-build.xml \
            --json-output=test-results/json/bazel-build.json

    - name: Upload test results
      uses: actions/upload-artifact@v4
      with:
        name: ci-dashboard-results
        path: test-results/
        if-no-files-found: ignore

    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v2
      with:
        files: "test-results/junit/*.xml"

GitLab CI
~~~~~~~~~

.. code-block:: yaml

    build_and_test:
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

Jenkins
~~~~~~~

.. code-block:: groovy

    stage('Build and Test') {
        steps {
            sh '''
                mkdir -p test-results/junit test-results/json
                poetry run python devops/remote_exec.py bazel build //... \\
                    --junit-output=test-results/junit/bazel-build.xml \\
                    --json-output=test-results/json/bazel-build.json
            '''
        }
        post {
            always {
                junit 'test-results/junit/*.xml'
                archiveArtifacts artifacts: 'test-results/**/*', fingerprint: true
            }
        }
    }

Processing Results
-----------------

Python Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

    import json
    import xml.etree.ElementTree as ET

    # Process JSON
    with open('test-results/bazel-build.json', 'r') as f:
        results = json.load(f)
    
    success_count = sum(1 for r in results if r['returncode'] == 0)
    print(f"Success rate: {success_count/len(results)*100:.1f}%")

    # Process JUnit XML
    tree = ET.parse('test-results/bazel-build.xml')
    root = tree.getroot()
    total_tests = int(root.get('tests'))
    failures = len(root.findall('testcase/failure'))
    print(f"Tests: {total_tests}, Failures: {failures}")

JavaScript Processing
~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

    // Load JSON results
    fetch('test-results/bazel-build.json')
        .then(response => response.json())
        .then(results => {
            const successful = results.filter(r => r.returncode === 0).length;
            const successRate = (successful / results.length) * 100;
            console.log(`Success rate: ${successRate.toFixed(1)}%`);
        });

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Missing dependencies:**
.. code-block:: bash

    poetry install --with dev

**Permission errors:**
.. code-block:: bash

    mkdir -p test-results/junit test-results/json
    chmod 755 test-results/

**Invalid output files:**
.. code-block:: bash

    # Validate XML
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('test-results/junit/bazel-build.xml')"
    
    # Validate JSON
    python3 -c "import json; json.load(open('test-results/json/bazel-build.json'))"

**Build tool not found:**
.. code-block:: bash

    # Check if build tool is installed
    which bazel
    which buck2
    which goma
    which reclient

File Organization
----------------

Recommended Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    test-results/
    ├── junit/
    │   ├── bazel-build.xml
    │   ├── buck2-build.xml
    │   ├── goma-build.xml
    │   └── reclient-build.xml
    ├── json/
    │   ├── bazel-build.json
    │   ├── buck2-build.json
    │   ├── goma-build.json
    │   └── reclient-build.json
    └── summary.md

Naming Conventions
~~~~~~~~~~~~~~~~~

* **JUnit XML**: ``{build-system}-{command}.xml``
* **JSON**: ``{build-system}-{command}.json``
* **Examples**: ``bazel-build.xml``, ``buck2-test.json``, ``goma-build.xml`` 