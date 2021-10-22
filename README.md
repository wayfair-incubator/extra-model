[![codecov](https://codecov.io/gh/wayfair-incubator/extra-model/branch/main/graph/badge.svg?token=HXSGN5IUzu)](https://codecov.io/gh/wayfair-incubator/extra-model)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![GitHub license](https://img.shields.io/github/license/wayfair-incubator/extra-model)](https://github.com/wayfair-incubator/extra-model/blob/main/LICENSE)
![PyPI](https://img.shields.io/pypi/v/extra-model)

Table of Contents
=================

* [extra\-model](#extra-model)
  * [Quick start](#quick-start)
    * [Using docker\-compose](#using-docker-compose)
      * [Downloading Embeddings](#downloading-embeddings)
      * [[Optional] Run docker\-compose build again](#optional-run-docker-compose-build-again)
      * [Run extra\-model](#run-extra-model)
  * [Learn more](#learn-more)
* [Authors](#authors)

# extra-model

Code to run the Extra [algorithm](https://www.aclweb.org/anthology/D18-1384/) for the unsupervised topic/aspect extraction on English texts.

[Read the Official Documentation here](https://wayfair-incubator.github.io/extra-model/site)

## Quick start


**IMPORTANT**:
1. When running Extra inside docker-container, make sure that Docker process has enough resources.
For example, on Mac/Windows it should have at least 8 Gb of RAM available to it. [Read More about RAM Requirements][ram_requirements]
1. GitHub repo does **not** come with Glove Embeddings. See section `Downloading Embeddings` for how to download the required embeddings.


### Using docker-compose

This is a preferred way to run `extra-model`. 
You can find instructions on how to run `extra-model` using CLI or as a Python package [here](https://wayfair-incubator.github.io/extra-model/site/running_extra/)  

First, build the image:

```bash
docker-compose build
```

Then, run following command to make sure that `extra-model` was installed correctly:

```bash
docker-compose run test
```

#### Downloading Embeddings

Next step is to download the embeddings (we use [Glove](https://nlp.stanford.edu/projects/glove/) from Stanford in this project).

To download the required embeddings, run the following command:

```bash
docker-compose run --rm setup
```

The embeddings will be downloaded, unzipped and formatted into a space-efficient format. Files will be saved in the `embeddings/` directory in the root of the project directory. If the process fails, it can be safely restarted. If you want to restart the process with new files, delete all files except `README.md` in the `embeddings/` directory.

#### [Optional] Run `docker-compose build` again

After you've downloaded the embeddings, you may want to run `docker-compose build` again. 
This will build an image with embeddings already present inside the image. 

The tradeoff here is that the image will be much bigger, but you won't spend ~2 minutes each time you run `extra-model` waiting for embeddings to be mounted into the container.
On the other hand, building an image with embeddings in the context will increase build time from ~3 minutes to ~10 minutes.

#### Run `extra-model`

Finally, running `extra-model` is as simple as:

```bash
docker-compose run extra-model /package/tests/resources/100_comments.csv
```

NOTE: when using this approach, input file should be mounted inside the container.
By default, everything from `extra-model` folder will be mounted to `/package/` folder.
This can be changed in `docker-compose.yaml`

This will produce a `result.csv` file in `/io/` (default setting) folder.

There are multiple flags you can set to change input/outputs of extra. You can find them by running:

```bash
docker-compose run extra-model --help
```

## Bumping model version

The package `bump2version` in order to automate the package version, [source](https://github.com/c4urself/bump2version).

With the current configuration (in the `setup.cfg` file), running the command 
```bash
bumpversion patch
```
will:
* Increase the model version in the file `extra_model/__init__.py`
* Increase the model version in the test file `tests/test_init.py`
* Create a commit with the modified files and message `Bump version: {old_version} → {new_version}`
* Tag the last commit as `v{new_version}`

In order to perform a dry run for the command above, execute:
```bash
bumpversion patch -n --verbose
```

## Learn more

Our [official documentation][official_documentation] is the best place to continue learning about `extra-model`:
1. [Explanation of inputs/outputs][official_documentation]
1. [Step-by-step workflow](https://wayfair-incubator.github.io/extra-model/site/workflow/) of what happens inside of `extra-model`
1. [Examples](https://wayfair-incubator.github.io/extra-model/site/examples/examples/) of how `extra-model` can be used in downstream applications
1. [Detailed explanation](https://wayfair-incubator.github.io/extra-model/site/running_extra/) of how to run `extra-model` using different interfaces (via `docker-compose`, via CLI, as a Python package).

# Authors

`extra-model` was written by `mbalyasin@wayfair.com`, `mmozer@wayfair.com`.

[official_documentation]: https://wayfair-incubator.github.io/extra-model/site
[ram_requirements]: https://wayfair-incubator.github.io/extra-model/site/ram_requirements
