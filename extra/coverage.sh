#!/bin/bash

DIR="/tmp/coverage-output"

coverage run setup.py nosetests
rm -rf "$DIR"
coverage html -d "$DIR" --include "petrel/*"
open "$DIR/index.html"