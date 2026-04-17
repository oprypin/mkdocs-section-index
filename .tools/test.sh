#!/bin/sh
set -e

cd "$(dirname "$0")/.."

properdocs build -f example/properdocs.yml --strict
