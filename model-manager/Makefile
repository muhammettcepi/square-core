SHELL := /bin/bash

# files to check for linting
SRC=$(shell find . -type f -name '*.py')

# files to check for quality
check_dirs := .

# global defs
.PHONY: quality lint

quality:
	isort --check ${check_dirs}
	black --check ${check_dirs}
	flake8 ${check_dirs}

lint: $(SRC)
	pylint $? --max-line-length=120

##		Install dependencies.
install:
	pip install --upgrade pip
	pip install -r requirements.txt

##		Install dependencies for development.
install-dev:
	pip install --upgrade pip
	pip install -r requirements.dev.txt

##		Setup authentication for local development.
auth:
	@square_pk
	@square_token

##		Generate and print an access token from the private key.
token:
	@square_token

##		Bring up the development environment.
up:
	docker compose --env-file .local.env up -d 

##		Bring down the development environment.
down:
	docker compose --env-file .local.env down
##		Build the development environment.

build:
	docker compose --env-file .local.env build 
##		Show logs from the development environment.

logs:
	docker compose --env-file .local.env logs -f maintaining_worker