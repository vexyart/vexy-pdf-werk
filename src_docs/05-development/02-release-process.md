# Release Process

This project uses a script to automate the release process. To create a new release, run the following command:

```bash
./scripts/release.sh <version>
```

For example:

```bash
./scripts/release.sh 1.2.0
```

This script will:

1.  Run all quality checks and tests.
2.  Build the package.
3.  Create a git tag for the new version.
4.  Push the changes and tag to the remote repository.
5.  Publish the package to Test PyPI and then to PyPI.
6.  Create a new release on GitHub.
