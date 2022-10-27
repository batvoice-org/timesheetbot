# TimesheetBot

Slack agent to prompt users for timesheets / automatically fill CIR-CII sheets

## Requirements

- Docker and docker-compose
- Have admin rights to a Slack App
- Have a GCP projet configured
  - Create a service account to edit a GSheet programatically

## Build / deploy

Login to your docker repository.

To build and push:
```bash
export DOCKER_IMAGE={MY_DOCKER_REGISTRY:MY_DOCKER_REPOSITORY}
make docker-build
make docker-push
```

Now, you must create a `values.yaml` file to override the default configuration `helm-chart/values.yaml` and configure the application. Please consult the default values.yaml file for a complete documentation.

Then use `helm` to deploy to a Kubernetes cluster:
```bash
helm upgrade \
--install \
--wait \
--atomic \
-f {PATH_TO_MY_SECRET_VALUES.yaml} \
timesheetbot
helm-chart/timesheetbot
```

## How to add / setup a new employee ?

TODO
