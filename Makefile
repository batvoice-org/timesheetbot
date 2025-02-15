PACKAGE ?= timesheetbot
DOCKER ?= $(shell which docker || echo docker)
DOCKER_IMAGE ?= 367353094751.dkr.ecr.eu-west-1.amazonaws.com/$(shell echo $(PACKAGE) | tr A-Z a-z)
VERSION ?= $(shell git describe 2>/dev/null || git rev-parse --short HEAD)
DOCKER_BUILD ?= $(DOCKER) image build
DOCKER_PUSH ?= $(DOCKER) image push
DOCKER_BUILD_FILE ?= Dockerfile
DOCKER_BUILD_OPTIONS ?= --build-arg IMAGE=$(DOCKER_IMAGE) --build-arg TAG=$(VERSION)

docker-aws-ecr-login:   ## Apply AWS credentials for the container registry to local docker.
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 367353094751.dkr.ecr.eu-west-1.amazonaws.com

docker-build:   ## Build a docker image.
	$(DOCKER_BUILD) -f $(DOCKER_BUILD_FILE) $(DOCKER_BUILD_OPTIONS) -t $(DOCKER_IMAGE):$(VERSION) -t $(DOCKER_IMAGE):latest .

docker-push: ## Push docker image to remote registry.
	$(DOCKER_PUSH) $(DOCKER_PUSH_OPTIONS) $(DOCKER_IMAGE):$(VERSION)
	$(DOCKER_PUSH) $(DOCKER_PUSH_OPTIONS) $(DOCKER_IMAGE):latest

update-main:
	# requirements.txt
	pip-compile $(PIP_COMPILE_OPTIONS) --verbose --upgrade --no-header --output-file .requirements.txt
	echo "# Generated $(shell date +'%F %T.%N')" > requirements.txt
	echo "# =======================================" >> requirements.txt
	echo "" >> requirements.txt
	cat .requirements.txt | grep -v "^--index-url" | grep -v "^--extra-index-url" >> requirements.txt
	rm .requirements.txt

update-dev:
	# requirements-dev.txt
	pip-compile $(PIP_COMPILE_OPTIONS) --extra "dev" --upgrade --no-header --output-file .requirements-dev.txt
	echo "# Generated $(shell date +'%F %T.%N')" > requirements-dev.txt
	echo "# =======================================" >> requirements-dev.txt
	echo "" >> requirements-dev.txt
	cat .requirements-dev.txt | grep -v "^--index-url" | grep -v "^--extra-index-url" >> requirements-dev.txt
	rm .requirements-dev.txt

update:
	make -j 2 update-main update-dev

help:   ## Shows available commands.
	@echo "Available commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?##[\s]?.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"}; {printf "	make \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
