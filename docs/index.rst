.. ai_native_systems documentation master file, created by
   sphinx-quickstart on Fri Jul 19 10:00:00 2025.
   You can adapt this file completely to your liking and it should at least
   contain the root `toctree` directive.

Welcome to AI-Native Systems's documentation!
============================================

AI-Native Systems is a modular architecture for building advanced, context-aware agents and tools. This scaffold is designed for rapid prototyping and research in AI-native software, combining Python and Rust for flexibility and performance.

Key Features
-----------

* **Remote Execution**: Support for Bazel, Buck2, Goma, and Reclient with CI Dashboard integration
* **Vector Store**: Embedding-based context recall with FAISS and sentence-transformers
* **Multi-Agent Orchestration**: AI-orchestrated development workflows
* **Meta-Prompting**: Self-reflective prompting strategies
* **CI/CD Integration**: JUnit XML and JSON output for comprehensive dashboard support

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   ci_dashboard
   ci_quick_reference

Quick Start
----------

.. code-block:: bash

    # Install dependencies
    poetry install

    # Run tests
    make test

    # Demonstrate CI Dashboard functionality
    make demo-ci-output

    # Generate CI output for build systems
    make bazel-ci

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
