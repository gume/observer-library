#!/bin/sh
# Build <name>-<version>.tgz from the repository (the format `observer library import` reads).
set -e
cd "$(dirname "$0")/.."
name=$(sed -n 's/^name: *//p' library.yaml)
version=$(sed -n 's/^version: *//p' library.yaml)
out="${1:-$name-$version.tgz}"
tar --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' -czf "$out" library.yaml README.md CHANGELOG.md tools skills
echo "$out"
