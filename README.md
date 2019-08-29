# LOVE Manager

This repository contains the code of the Django Channels project that acts as middleware for the LOVE-frontend

See the documentation here: https://lsst-ts.github.io/LOVE-manager/html/index.html

## 1. Use as part of the LOVE system
In order to use the LOVE-manager as part of the LOVE system we recommend to use the docker-compose and configuration files provided in the [LOVE-integration-tools](https://github.com/lsst-ts/LOVE-integration-tools) repo. Please follow the instructions there.

## 2. Local load for development
We provide a docker image and a docker-compose file in order to load the LOVE-manager locally for development purposes, i.e. run tests and build documentation.

This docker-compose does not copy the code into the image, but instead it mounts the repository inside the image, this way you can edit the code from outside the docker container with no need to rebuild or restart.

### 2.1 Load and get into the docker image
Follow these instructions to run the application in a docker container and get into it:

```
docker-compose up -d
docker-exec manager bash
```

### 2.2 Run tests
Once inside the container you will be in the `/usr/src/love/manager` folder, where you can run the tests as follows:
```
pytest
```

### 2.3 Build documentation
Once inside the container you will be in the `/usr/src/love/manager` folder, where you can move out to the `docsrc` folder and build the documentation as follows:
```
cd ../docsrc
./create_docs.sh
```
