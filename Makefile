
SHELL := /bin/bash

docker-build:
	docker build -t my-php-app .

docker-run-local: # docker-build
	docker run -it -p 8080:80 --env-file .env my-php-app

docker-run-bash: # docker-build
	docker run -it -p 8080:80 -env-file .env my-php-app bash

build-and-run: docker-build docker-run-local


# Cloud Run
deploy:
	bin/gcloud-run-deploy.sh

watch-gcs:
	watch gsutil -m ls gs://ricc-demos-386214-public-images/


# Watch this amazing bouncing error :)UO
