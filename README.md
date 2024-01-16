# Socker Manager

Soccer online manager game API

## Requirements

Install Docker on your machine

## Quick Start

In order to start backend locally you need to perform the following steps:

- Rename `.env.local` to `.env`
- Build docker image using `make build`
- Start the development server with `make up`

```bash
$ make build
$ make up
```

You can access your Django server http://localhost:8000/

## Project layout

- src/soccer - soccer manager implementation
- src/user - authentification (based on JWT)
- src/common - apps common stuff
- src/config/ - Django settings
- src/tests/ - tests

## Docker compose

The docker-compose file defines two services:

- A Postgres server
- An application server

## Makefile shortcuts

This project comes with a Makefile with several targets defined for the ease of development.

## Pre-commit

Install [pre-commit](https://pre-commit.com/) firstly.

Please execute `pre-commit install` once after downloading the repo code. It will help us keep the code quality in
check.

Run `pre-commit run --all-files` if you want to check your code

## Useful commands

Adding new production dependencies

```bash
docker-compose run app poetry add requests
```

Adding new development dependencies:

```bash
docker-compose run app poetry add requests -G dev
```

Recreating `poetry.lock` file

```bash
make lock
```
