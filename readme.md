# Warrens II
A Pygame based roguelike dungeon crawler. 
Second iteration of my earlier Warrens project moving back to a pygame only interface and away from the OpenGL interface (which was more effort than I could muster :)). The project was migrated to Python3.
Note that the main goal of this project is not to be a super compelling game :) It is a technical playground.

# Download
Want to have a look at what is going on here? Check out the project pages and grab a copy of the latest build :)
[https://frostlock.github.io/Warrens-II](https://frostlock.github.io/Warrens-II)

# Requirements
- Python 3
- pygame
- pyinstaller if you want to package the application (optional)
- Sphinx if you want to generate the documentation (optional) 

# Features

### Testing
This project is tested on Ubuntu 16.04, Mac OS 10.13 and Windows 2016 with Python versions 3.5, 3.6 and 3.7.
Testing is implemented using Azure Pipelines. 
Status of the latest test is directly below:  

[![Build Status](https://dev.azure.com/pboogaerts/Warrens-II/_apis/build/status/Frostlock.Warrens-II-Testing?branchName=master)](https://dev.azure.com/pboogaerts/Warrens-II/_build/latest?definitionId=4&branchName=master)

### Code
- Ported to Python 3
- More PEP 8 compliant, not entirely there yet :)
- Added unittests

### Game
- Basic audio
- Improved graphics

### Packaging
Packaged in a single file linux executable using pyinstaller.

### Documentation
Generated with Sphinx based on in code docstrings.