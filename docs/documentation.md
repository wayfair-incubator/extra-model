# Documentation

* Documentation is written in markdown format and files are kept in the `/docs` directory in the project root.
* New files must be added to the table of context in `index.md`.

## Development

Run the following command to render and serve documentation locally
```bash
docker-compose run --rm --service-ports mkdocs
```

The documentation will be available at `localhost:8000`

## Generation

Run the following command to render the documentation as `HTML` to the `/site` directory.

```bash
docker-compose run --rm mkdocs build
```

Github will automatically render contents from this directory at [https://wayfair-incubator.github.io/extra-model/](https://wayfair-incubator.github.io/extra-model/) once merged to the main branch.
