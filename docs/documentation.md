# Documentation

* Documentation is written in markdown format and files are kept in the `/docs` directory in the project root.
* New files must be added to the table of context in `/mkdocs.yml`.

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

This directory is ignored in all branches except `gh-pages` branch. Use the following instructions to commit changes to documentation:

1. Run `docker-compose run --rm mkdocs build` from the development branch.
2. Run `git checkout gh-pages` to switch to the `gh-pages` branch and commit changes to the `/site` directory on this branch.
3. Push your changes.

Github will automatically render contents at [https://wayfair-incubator.github.io/extra-model/](https://wayfair-incubator.github.io/extra-model/) but it may take up to 20 minutes for changes to appear.

