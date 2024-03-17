# Contributing to Dan's Log Formatter

Thank you for your interest in contributing to Dan's Log Formatter! This document will help guide you through the process.

## Reporting Bugs

> :warning: **WARNING**
>
> If you have discovered a security vulnerability, please **DO NOT** file a public issue.
> Instead, please report them directly to danyi1212@users.noreply.github.com.

If you have found a bug, we would like to know, so we can fix it! Before you file a bug report, please make sure that
the bug
can be reproduced consistently.

To report a bug, create a new GitHub Issue with the "bug" label. Make sure to include a minimal reproduction of the bug
and any steps needed to reproduce it.

Please feel free to discuss it in GitHub Discussions first. Other users may have experienced a similar issue and can
provide insights or guidance on how to overcome it.

## Asking Questions and Requesting Features

If you have any questions, ideas, or want to request a feature, feel free to discuss them in GitHub Discussions.

For feature requests, create a new GitHub Issue with the "enhancement" label after discussing it in GitHub Discussions.

## Contribution Process

To contribute to the project, follow these steps:

1. Fork the repository.
2. Create a branch with a descriptive name, using prefixes like `feature/` or `bug/` for the branch names.
3. Open a pull request to the main branch.
4. Check the CI workflow statuses and for comments on your pull request.

## Setting up a local development environment

#### Prerequisites

- Python
- An IDE (I use PyCharm, but you can choose your preferred IDE)

### Create dev environment

1. Clone your fork of the Dan's Log Formatter repository.
    ```shell
    git clone https://github.com/<your_username>/dans-log-formatter.git
    ```
2. Navigate to the root folder of the repository.
    ```shell
    cd dans_log_formatter/
    ```
3. Install the Python dependencies using Poetry.
    ```shell
    poetry install
    ```
4. Install pre-commit hooks
   ```shell
   pre-commit install
   ```

# License

Dan's Log Formatter is licensed under the [MIT License](LICENSE).
By contributing to this project, you agree to license your contribution under the same license as the project.

# Code of Conduct

Please note that the Dan's Log Formatter project is released with a Contributor Code of Conduct. By contributing to this
project, you agree to abide by its terms. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for more information.

# Contact

If you have any questions or concerns, feel free to contact @danyi1212.
