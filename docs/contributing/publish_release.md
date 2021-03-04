# Publish a Release

## Update Package Version

1. Create a version bump feature branch

        git checkout -b bump_version_v1.2.3

1. Update the package version in `/extra_model/__init__.py`

        __version__ = "1.2.3"

1. Update `CHANGELOG.md` in the project root

1. Update any documentation that mentions the package version

1. Commit and push the changes

        git add .
        git commit -m 'bumping version'
        git push -u origin bump_version_v1.2.3

1. Upon approval of the PR, merge changes to the `main` branch with the Github.com UI

1. Pull down the changes merged to the `main` branch

        git checkout main; git pull

## Publish Release with Github Action

1. Tag changes with the new version

        git tag v1.2.3
        git push origin v1.2.3

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
      