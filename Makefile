PARTITIONS=1
REPLICATION-FACTOR=1

# For local development
export WORKER_PORT=6066
export SIMPLE_SETTINGS=integrated_data_processing.settings

PYTHON?=python

# Installation
install:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r ./requirements/base.txt

install-windows:
	$(PYTHON) -m venv venv
	.\venv\Scripts\activate
	pip install -r .\requirements\base.txt
	.\venv\Scripts\activate

install-test:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r ./requirements/test.txt

install-production:
	$(PYTHON) -m venv ./venv
	./venv/bin/pip install -U pip -r ./requirements/production.txt

bash:
	docker-compose run --user=$(shell id -u) ${service} bash

# Build docker compose
restart:
	docker-compose restart ${service}

logs:
	docker-compose logs

# Removes old containers, free's up some space
remove:
	# Try this if this fails: docker rm -f $(docker ps -a -q)
	docker-compose rm --force -v

remove-network:
	docker network rm integrated_data_processing_default || true

stop:
	docker-compose stop

stop-kafka-cluster: stop remove remove-network


# Faust commands related
start-app:
	./scripts/run
start-app-windows:
	./scripts/run_windows


# Build docker image
build:
	docker build -t integrated_data_processing .

run:
	docker run integrated_data_processing


serve-model:
	./scripts/serve_model

run-tests:
	./scripts/test
