#!/usr/bin/env bash

docker-compose run --rm mkdocs build
git add site
git stash
git checkout gh-pages
git checkout stash -- site
git commit -m 'updating documentation'
git push
git checkout main
