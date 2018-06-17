OpenDataCube Product Loader v0.1 Beta

Prerequisites
1. QGIS 3
2. Datacube-core python package
3. A populated and running local Open Data Cube instance  

This plugin uses Datacube module and PostgreSql database to load information about indexed and ingested data products, plot products using matplotlib and convert ingested products to raster form and display in QGIS.

Steps to load data:-

1. Connect Database Server
2. Browse information on products in Product Information View
3. Choose product name to be plotted or loaded in the Products View
4. Input the resolution of the product to be plotted or displayed.
5. Either input coordinates yourself or click on "Select coordinates on canvas" button to show ingested data coordinates in a raster/vector layer on QGIS canvas. You can use [use default] button to use pre-loaded vector layer given along the plugin.
6. To plot data click on Plot Data button. If you need Column Wrap to define the number of columns to display plotted datasets and column name such as time, solar day,etc.
7. To load raster layer, origin coordinates are required with the path[folder] to store ingested data-set as a raster layer in QgisInterface. 

Note:- Please plot or load one product at a time to avoid plugin crash.
