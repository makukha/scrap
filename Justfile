# init local dev environment
sync:
    uv sync

# build python package
build:
    uv lock
    uv build

# publish package on PyPI
[group('release')]
push-pypi:
    rm -rf dist
    @just build
    uv publish
