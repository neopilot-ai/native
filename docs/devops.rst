
devops package
==============

The devops package provides remote execution capabilities and CI Dashboard integration for build systems.

Remote Execution CLI
-------------------

The remote execution CLI supports Bazel, Buck2, Goma, and Reclient with JUnit/JSON output for CI dashboards.

.. automodule:: devops.remote_exec
   :members:
   :undoc-members:
   :show-inheritance:

CI Dashboard Integration
-----------------------

The project includes comprehensive CI Dashboard integration with:

* **JUnit XML Output**: Standard format for CI platforms
* **JSON Output**: Machine-readable format for custom dashboards
* **CLI Integration**: All build commands support output generation
* **CI Workflow Integration**: Automated test result generation and artifact upload

For detailed documentation, see :doc:`ci_dashboard`.

Usage Examples
-------------

.. code-block:: bash

    # Generate both JUnit XML and JSON output
    poetry run python devops/remote_exec.py bazel build //... \
        --junit-output=test-results/bazel-build.xml \
        --json-output=test-results/bazel-build.json

    # Use Makefile shortcuts
    make bazel-ci      # Creates bazel-build.xml + bazel-build.json
    make buck2-ci      # Creates buck2-build.xml + buck2-build.json
    make goma-ci       # Creates goma-build.xml + goma-build.json
    make reclient-ci   # Creates reclient-build.xml + reclient-build.json

    # Demonstrate functionality
    make demo-ci-output
