# Publish a Release

## Update Package Version

1. Create a version bump feature branch

        git checkout -b bump_version_v1.2.3

1. Update `CHANGELOG.md` in the project root

1. Update any documentation that mentions the package version

1. Commit the changes to your local repository

        git add .
        git commit -m 'some brief description of the changes'

1. This library uses the package `bump2version` to automate its versioning, [source](https://github.com/c4urself/bump2version).

For example, with the current configuration (in the `setup.cfg` file), running the command 
```bash
bumpversion major|minor|patch
```
will:
* Increase the model major|minor|patch version in the file `extra_model/__init__.py`
* Increase the model major|minor|patch version in the test file `tests/test_init.py`
* Create a commit with the modified files and message `Bump version: {old_version} → {new_version}`
* Tag the last commit as `v{new_version}`

In order to perform a dry run for the command above, execute:
```bash
bumpversion major|minor|patch -n --verbose
```

Please notice that the git working directory is expected to be clean when running `bumpversion`.

Choose the major|minor|patch argument according to the importance of the changes. 
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

1. After successfully running `bumpversion`, please run `git push && git push --tags` to synchronize the local repository with the remote one.

1. Create a PR. Upon approval of the PR, merge changes to the `main` branch with the Github.com UI

1. Pull down the changes merged to the `main` branch

        git checkout main; git pull

## Publish Release with Github Action

1. Visit the [`extra-model` repository][repo]

1. Under **Releases** in the right column, visit `Create a new release`

1. Enter the tag version you previously created in the `Tag version` input, and 
  make sure the `main` branch is selected. Title and description are optional.
  
1. Press **Publish Release** at the bottom.

1. Visit **Actions** in the top navigation of the Github.com UI

1. Visit on the most recent workflow run. This run represents the Github Action that is building, testing, and publshing the package release to PyPI.

1. The publish action requires approval before publishing to PyPI. Click **Review Deployments** on the right side of the yellow notification bar.

1. Select the **Publish Release** checkbox and click **Approve and Deploy** to unblock the deployment.

1. The package will now be built, tested, and depoyed to PyPI! The new package version will be live once the pipeline completes.

[repo]: https://github.com/wayfair-incubator/extra-model
      