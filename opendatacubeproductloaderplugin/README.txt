OpenDataCube Product Loader v0.1 Beta

Prerequisites
1. QGIS 3
2. Datacube-core python package
3. A populated and running local Open Data Cube instance  

Installation for Windows
  1.Installation with OSGeo4W

  2.Run osgeo4w-setup-x86_64.exe and select Advanced install

  3.Install QGIS 3.x from the Desktop section.

  4.Download the appropriate rasterio wheel from the Unofficial Windows Binaries for Python Extension Packages site

  5.Open an OSGeo4W shell and type the following

  C:\> pip3 install <path to download folder>\rasterio-1.0a12-cp36-cp36m-win_amd64.whl
  C:\> pip3 install datacube
  
Note: You may need to install updated GDAL, numpy and pandas from the above site.

This plugin uses Datacube module and PostgreSql database to load information about indexed and ingested data products, plot products using matplotlib and convert ingested products to raster form and display in QGIS.

Steps to load data:-

1. Connect Database Server
2. Browse information on products in Product Information View
3. Choose product name to be plotted or loaded in the Products View
4. Input the resolution of the product to be plotted or displayed.
5. Either input coordinates yourself or click on "Select coordinates on canvas" button to show ingested data coordinates in a raster/vector layer on QGIS canvas.
6. Input other relevant information to either plot or view data in QGIS map canvas.

Note:- Please plot or load one product at a time to avoid plugin crash.
