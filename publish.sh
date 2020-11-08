#!/bin/bash
set -euxo pipefail

pushd build

git init -b gh-pages
git add .
git commit -m "Publish commit"

git remote add origin git@github.com:miskosz/covid-weekly.git
git push --force origin gh-pages

popd
