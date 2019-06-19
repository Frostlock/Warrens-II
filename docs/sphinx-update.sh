#!/usr/bin/env bash
make clean
sphinx-apidoc -f -o source/ ../../Warrens-II/src/
make html