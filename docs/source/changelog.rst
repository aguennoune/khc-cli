Changelog
=========
History of changes for KHC CLI versions.

* **1.17.0** (2025-06-05): Major project restructuring and enhancements
  - Restructured project to eliminate src/ directory for simpler imports and installation
  - Added YAML-based user configuration system via ~/.khc_cli_rc
  - Implemented config init command to generate and manage user configuration
  - Updated documentation to reflect new structure and configuration options
  - Optimized entry point script for better error handling and path resolution
  - Standardized all docstrings and comments in English
  - Cleaned up code and dependencies for better maintainability

* **0.5.1** (2025-06-01): Initial release
* **1.1.16** (2025-06-04): Improved error handling for invalid commands and added more detailed helpers options.
* **0.2.0-alpha.2** (2025-06-04):  
  - Added English docopt-style docstrings for all CLI commands (`analyze.py`, `curate.py`, `etl.py`)
  - Improved documentation for Read The Docs
  - Updated versioning for pre-release consistency
  - Minor code and documentation cleanups

Command Usage Docstrings (docopt style)
=======================================

analyze.py
----------

.. code-block:: text

    KHC CLI - analyze command
    Usage:
      khc-cli analyze repo <repo_name> [--format=<format>] [--github-api-key=<key>]
      khc-cli analyze etl [--awesome-repo-url=<url>] [--output-dir=<dir>] [--github-api-key=<key>] [--use-template/--no-use-template]

    Options:
      -h --help                 Show this help message
      -f --format=<format>      Output format (table, json) [default: table]
      --github-api-key=<key>    GitHub API Key
      --awesome-repo-url=<url>  URL of the Awesome list to analyze
      --output-dir=<dir>        Output directory [default: ./csv]
      --use-template            Use the Awesome List template [default: True]

    Description:
      Analyze GitHub repositories and run an ETL pipeline on Awesome lists.

curate.py
---------

.. code-block:: text

    KHC CLI - curate command
    Usage:
      khc-cli curate validate <readme_path>
      khc-cli curate add_project <repo_url> [--readme-path=<path>] [--section=<section>] [--github-api-key=<key>]

    Options:
      -h --help                  Show this help message
      --readme-path=<path>       Path to the README.md [default: README.md]
      --section=<section>        Section where to add the project
      --github-api-key=<key>     GitHub API Key

    Description:
      Validate and enrich Awesome lists (add projects, format validation).

etl.py
------

.. code-block:: text

    KHC CLI - ETL pipeline
    Usage:
      khc-cli analyze etl [--awesome-repo-url=<url>] [--output-dir=<dir>] [--github-api-key=<key>] [--use-template/--no-use-template]

    Options:
      -h --help                 Show this help message
      --awesome-repo-url=<url>  URL of the Awesome list to process
      --output-dir=<dir>        Output directory [default: ./csv]
      --github-api-key=<key>    GitHub API Key
      --use-template            Use the Awesome List template [default: True]

    Description:
      ETL pipeline to extract, transform, and load data from an Awesome list.
