#!/bin/bash -xe

source /opt/config/basics.sh

jekyll new myblog
jekyll serve -H 0.0.0.0

echo done
