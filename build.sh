#!/bin/bash

tar_extra='--exclude-vcs --exclude-vcs-ignores --exclude=build.sh'

[[ ! -d dist ]] && mkdir dist
makeself.sh --tar-extra "$tar_extra" ~/dev/myd0t/ dist/myd0t.run myd0t ./myd0t.py

echo 'created dist/myd0t.run'
