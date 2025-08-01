# Contributing to Arbitrary Session Management

Contributions to Arbitrary Session Management are welcome from all!

Arbitrary Session Management is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/arbitrary-session-management).

Arbitrary Session Management follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

Please remember to sign off your commits (e.g., by using `git commit -s` if you
are using the command line client). This amends your git commit message with a line
of the form `Signed-off-by: Name Lastname <name.lastmail@emailaddress.com>`. Please
include all authors of any given commit into the commit message with a
`Signed-off-by` line. This indicates that you have read and signed the Developer
Certificate of Origin (see below) and are able to legally submit your code to
this repository.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

# Getting Started

## Prerequisites

- (Optional) Install [Visual Studio Code](https://code.visualstudio.com/download).
- Install [Git](https://git-scm.com/downloads).
- Install Python and add it to the `PATH`. [Version 3.9 or later](https://www.python.org/downloads/release/python-390)
- Install Poetry. [Version 2.0.1 or later](https://python-poetry.org/docs/#installation)

## Clone or Update the Git Repository

To download the Arbitrary Session Management source, clone its Git
repository to your local PC.

```cmd
git clone https://github.com/ni/arbitrary-session-management.git
```

If you already have the Git repository on your local PC, you can update it.

```cmd
git checkout main
git pull
```

## Select a Package/Module to Develop

Open a terminal window and `cd` to the package that you want to develop.

```cmd
cd <package/module>
```

## Install the Dependencies

From the subdirectory, run the [`poetry install`](https://python-poetry.org/docs/cli/#install)
command. This creates an in-project virtual environment (`.venv`) and installs
the package's dependencies and dev-dependencies, as specified in its
`pyproject.toml` and `poetry.lock` files.

```cmd
poetry install
```

## Activate the Virtual Environment (If Needed)

- (Preferred) Prefix commands with `poetry run`, e.g. `poetry run python server.py`
- In VS Code ([link](https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment))

# Update gRPC Stubs (If Needed)

The `src/server` and `src/client` directories contain the
auto-generated Python files based on (`.proto`) file. The following files need
to be replaced whenever there is a change to this [`server.proto`](src/server/json_logger.proto) or [`client.proto`](src/client/client_session/json_logger.proto) files:

- [server stubs](src/server/stubs/)
- [client stubs](src/client/client_session/stubs/)

To regenerate the gRPC stubs, `cd` to the directory, install
it with `poetry install`, and run `poetry run python -m grpc_tools.protoc --proto_path=. --python_out=<stubs_directory> --grpc_python_out=<stubs_directory> --mypy_out=<stubs_directory> --mypy_grpc_out=<stubs_directory> <proto_file_path>`.

Update your import statements in your component or implementation as needed. For reference:

- [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.py](https://github.com/ni/arbitrary-session-management/blob/main/src/server/stubs/json_logger_pb2_grpc.py#L6)
- [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.pyi](https://github.com/ni/arbitrary-session-management/blob/main/src/server/stubs/json_logger_pb2_grpc.pyi#L26)
- [stubs directory is a package and the component is also a Python package - <proto_file_name>_pb2_grpc.py](https://github.com/ni/arbitrary-session-management/blob/main/src/client/client_session/stubs/json_logger_pb2_grpc.py#L6)
- [stubs directory is a package and the component is also a Python package - <proto_file_name>_pb2_grpc.pyi](https://github.com/ni/arbitrary-session-management/blob/main/src/client/client_session/stubs/json_logger_pb2_grpc.pyi#L26)

# Lint and Build Code

## Lint Code for Style and Formatting

Use [ni-python-styleguide](https://github.com/ni/python-styleguide) to lint the
code for style and formatting. This runs other tools such as `flake8`,
`pycodestyle`, and `black`.

```cmd
poetry run ni-python-styleguide lint
```

If there are any failures, try using `ni-python-styleguide` to fix them, then
lint the code again. If `ni-python-styleguide` doesn't fix the failures, you
will have to manually fix them.

```cmd
poetry run ni-python-styleguide fix
poetry run ni-python-styleguide lint
```

## Mypy Type Checking

Use [Mypy](https://pypi.org/project/mypy/) to type check the code.

```cmd
poetry run mypy
```

## Bandit Security Checks

Use [Bandit](https://pypi.org/project/bandit/) to check for common security issues.

```cmd
poetry run bandit -c pyproject.toml -r <directory_path>
```

## Build Distribution Packages

To build distribution packages, run `poetry build`. This generates installable
distribution packages (source distributions and wheels) in the `dist`
subdirectory.

```cmd
poetry build
```

# Adding Dependencies

You can add new dependencies using `poetry add` or by editing the `pyproject.toml` file.

When adding new dependencies, use a `>=` version constraint (instead of `^`)
unless the dependency uses semantic versioning.

# Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/<reponame>/blob/main/LICENSE)
for details about how Arbitrary Session Management is licensed.
