The documentation for this project is generated using Sphinx.
This file contains some notes on how to setup Pycharm with Sphinx to generate the documentation.

# Helpful
https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/


# Installation
sudo pip3 install Sphinx

# Configuration

## Initial quickstart
Settings -> Tools -> Pycharm integrated tools ->
set working directory for sphinx: <full path here>/Warrens-II/util/sphinx

pycharm -> Tools > Sphinx quickstart 

This will generate a conf.py file

## Fine tune the sphinx conf.py

Add 'sphinx.ext.autodoc' to the Sphinx extensions in docs/source/conf.py  
`
extensions = ['sphinx.ext.autodoc']
`

Uncomment the path setup, it should look like this:  
`
import os
import sys  
sys.path.insert(0, os.path.abspath('../../../src/'))
`

## Pycharm documentation task
Nex step would be to create a pycharm documentation task
* You can configure a Sphinx documentation task in the run configurations.
set the input path to the Sphinx source folder
set the output path to the Sphinx build folder
set the working directory to the project root folder

* Unfortunately, currently there is an issue in sphinx_runner.py
https://youtrack.jetbrains.com/issue/PY-35091
This is hopefully fixed in future Pycharm versions.

* Before generating the docs the API stubs need to be created
sphinx-apidoc -o source/ ../src
(note that this only recognise proper python modules, meaning you need to have __init__.py for subfolders)

For the above reasons I found it easier to create a bash script that runs sphinx

# Integration with Github pages
On the GitHub website, go to the project settings
- activate GitHub pages
- set it to get docs from master branch in /docs folder

Disable jekyll (we are working with sphinx generated pages) by creating a .nojekyll file in the /docs folder

The Sphinx documentation from the /docs folder will now be used to generate a website:
https://frostlock.github.io/Warrens-II