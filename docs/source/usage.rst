Usage
=====

Basic usage examples for KHC CLI.

.. code-block:: bash

    khc-cli --help
    khc-cli analyze repo owner/repo

User configuration
------------------

KHC CLI can be configured via a YAML file `~/.khc_cli_rc` in your home directory.

To generate a default configuration file:

.. code-block:: bash

   khc-cli config init

You can force regeneration with:

.. code-block:: bash

   khc-cli config init --force

Example file structure:

.. code-block:: yaml

   version: 1.0
   config:
     default_output_format: markdown
     cache_dir: ~/.cache/khc-cli
     log_level: info
     api_keys:
       github: ""
   commands:
     analyze:
       description: "Analyze a GitHub repository or an Awesome list"
       usage: "khc-cli analyze [OPTIONS] TYPE TARGET"
       options:
         --format: "Output format (markdown, json, csv)"
         --output: "Output file (default: stdout)"

KHC CLI loads this configuration automatically at startup.
