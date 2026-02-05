#!/bin/bash

CONTAINER_CMD=$(which podman || which docker)

$CONTAINER_CMD tag registry.bristolhackspace.org/website:staging registry.bristolhackspace.org/website:live

$CONTAINER_CMD push registry.bristolhackspace.org/website:live

