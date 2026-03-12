#!/bin/bash

CONTAINER_CMD=$(which podman || which docker)

DATE_TAG=$(date +%Y%m%d)

$CONTAINER_CMD tag registry.bristolhackspace.org/website:staging registry.bristolhackspace.org/website:live
$CONTAINER_CMD tag registry.bristolhackspace.org/website:staging registry.bristolhackspace.org/website:$DATE_TAG

$CONTAINER_CMD push registry.bristolhackspace.org/website:live
$CONTAINER_CMD push registry.bristolhackspace.org/website:$DATE_TAG

