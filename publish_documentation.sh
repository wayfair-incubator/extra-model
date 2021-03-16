#!/usr/bin/env bash

git checkout main
git pull
docker-compose run --rm mkdocs build
git add site
git stash
git checkout gh-pages
git checkout stash -- site
git commit -m 'updating documentation'
git push --force
git checkout main
