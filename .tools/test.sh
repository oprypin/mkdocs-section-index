#!/bin/sh
set -e

cd "$(dirname "$0")/.."

mkdocs build -f example/mkdocs.yml --strict
