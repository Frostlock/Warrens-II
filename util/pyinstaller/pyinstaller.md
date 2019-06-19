This project uses PyInstaller to package a standalone application for easier distribution.
This file contains some notes on how PyInstaller is used.

# Installation on Linux
In theory this is enough
`sudo pip3 install pyinstaller`

I also needed
`sudo pip3 install --upgrade setuptools`

If you have both python 2 and 3 running in parallell, make sure to use the pip3 version.
I struggled with some packaging issues because pyinstaller was running under python 2 and 
thus pulling in python 2 libraries.

# Specifically for pygame
I ran into this issue
https://stackoverflow.com/questions/49165454/error-after-creating-executable-pygame-with-pyinstaller
Slightly different approach to fonts solved this. 

The game assets also need to be added in the pyinstaller spec file.

# Usage
The pyinstaller-package.sh script can be used to generate the distribution package. 
It will create a ./build working directory and a ../dist distribution directory.
Note that the./build working directory is excluded from Git. 


