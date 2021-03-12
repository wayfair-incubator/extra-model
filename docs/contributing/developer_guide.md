## CI

This project comes with a GitHub Actions pipeline definition. 

## Develop

First, please [install docker](https://docs.docker.com/install/) on your computer.
Docker must be running correctly for these commands to work. 

* If you are using windows, please make sure your editor writes files with the linefeed (`\n`) line endings.

Next, clone the repo:

TODO: update this

```bash
git clone 
cd extra-model
```

Then build an image:

```bash
docker-compose build
```

Then run the test suite to see if docker is set up correctly:

```bash
docker-compose run test
```

You are now set to work on your feature.

## Testing

You'll be unable to merge code unless the linting and tests pass. You can run these in your container via `docker-compose run test`.

The tests, linting, and code coverage are run automatically via CI, and you'll see the output on your pull requests.

Generally we should endeavor to write tests for every feature. 
Every new feature branch should increase the test coverage rather than decreasing it.

We use [pytest](https://docs.pytest.org/en/latest/) as our testing framework.

To test/lint your project, you can run `docker-compose run test`.

### Stages

To customize / override a specific testing stage, please read the documentation specific to that tool:

1. PyTest: [https://docs.pytest.org/en/latest/contents.html](https://docs.pytest.org/en/latest/contents.html)
1. Black: [https://black.readthedocs.io/en/stable/](https://black.readthedocs.io/en/stable/)
1. Flake8: [http://flake8.pycqa.org/en/latest/](http://flake8.pycqa.org/en/latest/)
1. Bandit: [https://bandit.readthedocs.io/en/latest/](https://bandit.readthedocs.io/en/latest/)
1. iSort: [https://pycqa.github.io/isort/](https://pycqa.github.io/isort/)
1. pydocstyle: [http://www.pydocstyle.org/en/stable/](http://www.pydocstyle.org/en/stable/)
