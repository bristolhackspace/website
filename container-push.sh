#!/bin/bash

CONTAINER_CMD=$(which podman || which docker)

$CONTAINER_CMD tag localhost/website:staging registry.bristolhackspace.org/website:staging

$CONTAINER_CMD push registry.bristolhackspace.org/website:staging

