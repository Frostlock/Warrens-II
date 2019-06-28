#!/usr/bin/env bash
make clean
sphinx-apidoc -f -o source/ ../../src/
make html
cp -r ./build/html/* ../../docs