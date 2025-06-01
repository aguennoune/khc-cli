## KHC CLI

# KHC CLI

[![PyPI version](https://img.shields.io/pypi/v/khc-cli.svg)](https://pypi.org/project/khc-cli/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/khc-cli.svg)](https://pypi.org/project/khc-cli/)
[![GitHub Stars](https://img.shields.io/github/stars/Krypto-Hashers-Community/khc-cli.svg?style=social)]
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/khc-cli.svg)](https://pypi.org/project/khc-cli/)
[![Documentation Status](https://readthedocs.org/projects/khc-cli/badge/?version=latest)](https://khc-cli.readthedocs.io/en/latest/?badge=latest)

Command-line tool for analyzing and curating Awesome lists, specialized for sustainable and open source technologies.

## Installation

```bash
pip install khc-cli
```

## Version

```bash
khc-cli --version
```
## Help

```bash
khc-cli --help
```
## Commandes

### GitHub API check Status

```bash
khc-cli status
```

## Templates

The `khc-cli` uses a curated template structure for analyzing and organizing Awesome lists. 
This template focuses on sustainable technologies categories and helps structure the analysis results.

For developers: The template file is included as a resource in the package and is used by the 
`analyze` and `curate` commands.

### Awesome List Analysis

```bash
khc-cli analyze <url_github>
```

### More Options

```bash
khc-cli analyze --help
```

## Documentation
For more information, please refer to the [Read The Docs](https://khc-cli.readthedocs.io/en/latest/).

## Development

To contribute to the project:

```bash
# Cloner le dépôt
git clone https://github.com/Krypto-Hashers-Community/khc-cli.git
cd khc-cli

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances de développement
pip install -e ".[dev]"
```

## Contributing
We welcome contributions to KHC CLI! If you have suggestions for improvements or new features, please follow these steps:

1. Fork the repository on GitHub.
2. Clone your forked repository.
3. Create a new branch for your feature or bug fix.
4. Make your changes and commit them.
5. Push your changes to your forked repository.
6. Create a pull request to the main repository.
7. Ensure your code passes all tests and adheres to the project's coding standards.
8. Wait for review and feedback from the maintainers.
9. Address any feedback and make necessary changes.
10. Once approved, your changes will be merged into the main branch.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

KHC CLI is a command-line interface tool designed to facilitate the analysis and curation of Awesome lists, with a particular focus on open sustainable technology.

## References to the Open Source Community

Thanks to the Open Source Community that is involved in gathering projects that preserve natural ecosystems through open technology, methods, data, intelligence, knowledge or tools.
