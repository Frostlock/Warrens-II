The documentation for this project is generated using Sphinx.
This file contains some notes on how to setup Pycharm wiht Sphinx to generate the documentation.

# Helpful
https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/


# Installation & configuration
sudo pip3 install Sphinx

Settings -> Pycharm integrated tools ->
set working directory for sphinx: <full path here>/Warrens-II/docs

pycharm -> Tools > Sphinx quickstart 
set source code directory to: .. 

Configure a Sphinx documentation task in the run configurations.
set the input path to the Sphinx source folder
set the output path to the Sphinx build folder
set the working directory to the project root folder

There is an issue in sphinx_runner.py
https://youtrack.jetbrains.com/issue/PY-35091
This is hopefully fixed in future Pycharm versions.

Before generating the docs the API stubs need to be created
sphinx-apidoc -o source/ ../../Warrens-II/
(note that this only recognise proper python modules, meaning you need to have __init__.py for subfolders)

Add 'sphinx.ext.autodoc' to the Sphinx extensions in docs/source/conf.py

Make sure the pathsetup in docs/source/conf.py is uncommented and properly points to the sources root.
import os
import sys
sys.path.insert(0, os.path.abspath('.'))


If things go wrong you can use the make command in the /docs folder 
make clean 
make html

# Usage
delete everyting in the docs/build directory (alternatively use make clean)
delete the *.rst files except index.rst
Recreate the rst files: sphinx-apidoc -f -o source/ ../../Warrens-II/
run the pycharm task for sphinx
