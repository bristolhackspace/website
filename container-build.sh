#!/bin/bash

CONTAINER_CMD=$(which podman || which docker)

$CONTAINER_CMD build -t localhost/website:staging -f Dockerfile

