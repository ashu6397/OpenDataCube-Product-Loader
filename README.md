# OpenDataCube Product Loader 

## Overview
An experimental QGIS plugin that performs the three basic functions:
* Visualize ingested data in datacube
* Plot ingested data
* Load ingested data in QGIS Map Interface as a Raster Layer

![alt text](https://github.com/ashu6397/OpenDataCube-Product-Loader/blob/master/opendatacubeproductloaderplugin/assets/Plugin%20Dialog.PNG)

## Requirements

### System
* QGIS 3.0+
* datacube-core python package
* A populated and running local `Open Data Cube` instance

## Installation
Installation procedure is same as in [Data Cube Query Installation](http://datacube-qgis.readthedocs.io/en/latest/installation.html)

#### Linux
Installation with `pip`:

- Install `QGIS` 3.0 via your distribution package manager
- Install the datacube-core package which will also install the required dependencies

        $ pip3 install datacube

Installation with `conda`:

- Install `miniconda` if you haven't already
- Create a QGIS + Data Cube environment

        $ conda create  -c conda-forge -n qgiscube python=3.6 qgis=3 datacube
        $ source activate qgiscube
        $ qgis

#### Windows
Installation with `OSGeo4W`

- Run `osgeo4w-setup-x86_64.exe` and select Advanced install
- Install QGIS 3.x from the Desktop section.
- Download the appropriate `rasterio` wheel from the
  [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio>)
  site
- Open an OSGeo4W shell and

        C:\> pip3 install <path to download folder>\rasterio-1.0a12-cp36-cp36m-win_amd64.whl
        C:\> pip3 install datacube

    Note: You *may* need to install updated GDAL, numpy and pandas from the above site.


### Plugin
- Download the latest `release` of the plugin
- Install the plugin in QGIS using `Plugins | Manage and Install Plugins... | Install from ZIP`


## Usage
Read this [document](https://github.com/ashu6397/OpenDataCube-Product-Loader/blob/master/opendatacubeproductloaderplugin/README.txt) for installation & usage of the plugin.


## Links
- [PostgreSql](https://www.postgresql.org/download/)
- [OpenDataCube Project](https://github.com/opendatacube)
- [OpenDataCube (Data Cube Query)](https://github.com/opendatacube/datacube-qgis)


## License
This plugin is licensed under GNU GPL v3.0. You can read the license [here](https://github.com/ashu6397/OpenDataCube-Product-Loader/blob/master/LICENSE)
