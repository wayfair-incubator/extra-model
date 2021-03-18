### Using docker-compose

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

Location of the output can be changed by supplying second path, e.g.:

```bash
docker-compose run extra-model /package/tests/resources/100_comments.csv /io/another_folder
```

The output filename can also be changed if you want it to be something else than `result.csv` by supplying a third argument:

```bash
docker-compose run extra-model /package/tests/resources/100_comments.csv /io/another_folder another_filename.csv
```

### Using command line

#### Install `extra-model`

First, install `extra-model` via pip:

```bash
pip install extra-model
```

#### Downloading Embeddings

Next, run the following to download and set up the required embeddings (we use [Glove](https://nlp.stanford.edu/projects/glove/) from Stanford in this project):

```bash
extra-model-setup
```

The embeddings will be downloaded, unzipped and formatted into a space-efficient format and saved in `/embeddings`.

If the process fails, it can be safely restarted. If you want to restart the process with new files, delete all files except `README.md` in the embeddings' directory.

#### Run `extra-model`

Once set up, running `extra-model` is as simple as:

```bash
extra-model tests/resources/100_comments.csv
```

This will produce a `result.csv` file in `/io`. If you want to change the output directory this can be done by providing it as a second argument to `extra-model` like so:

```bash
extra-model tests/resources/100_comments.csv /path/to/store/output
```

The output filename can also be changed if you want it to be something else than `result.csv` by supplying a third argument to `extra-model`:

```bash
docker-compose run extra-model tests/resources/100_comments.csv /path/to/store/output another_filename.csv
```

### Using as a Python package

#### Install `extra-model`

First, install `extra-model` via pip:

```bash
pip install extra-model
```

#### Downloading Embeddings

Next, use either the `extra-model-setup` CLI or `docker-compose` to download and set up the required embeddings (we use [Glove](https://nlp.stanford.edu/projects/glove/) from Stanford in this project):

```bash
extra-model-setup
```

or

```bash
docker-compose run --rm setup
```


The embeddings will be downloaded, unzipped and formatted into a space-efficient format. For the Docker based workflow, the embeddings will be saved to the `embeddings` directory. For the CLI workflow, by default, files will be saved in `/embeddings`. You can set another directory by providing it as an argument when running `extra-model-setup` like so:

```bash
extra-model-setup /path/to/store/embeddings
```


If the process fails, it can be safely restarted. If you want to restart the process with new files, delete all files except `README.md` in the embeddings' directory.

#### Use `extra-model` as a Python package

Once set up, you can use `extra-model` by calling the `run()` function in `extra_model/_run.py` :

```python
from extra_model._run import run

run(
    input_path=Path("input/path/file.csv"),
    output_path=Path("output/path")
)
```

This will process `input/path` and produce a `result.csv` file in `output/path`. If you want to change the output filename to be something different from `result.csv`, you can do os by providing an additional argument to `run()`:

```python
from extra_model._run import run

run(
    input_path=Path("input/path"),
    output_path=Path("output/path"),
    output_filename=Path("output_filename.csv")
)
```

