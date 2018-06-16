# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenDataCubeProductLoader
                                 A QGIS plugin
 This plugin visualizes, plot and loads ingested data as raster layer in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-06-14
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Ashutosh Vaish
        email                : ashutoshvaish6397@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QDir, Qt, QFileInfo,QVariant,QUrl,pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction,QMessageBox,QPushButton,QTreeWidget,QTreeWidgetItem,QApplication
from PyQt5.QtQuick import QQuickView
from qgis.core import QgsRasterLayer, QgsProject,QgsVectorLayer, QgsFields,QgsField,QgsFeature,QgsGeometry,QgsCoordinateReferenceSystem
from qgis.gui import QgsFileWidget,QgsProjectionSelectionWidget,QgsMapCanvas,QgsMapToolIdentifyFeature,QgsMapTool

# Initialize Qt resources from file resources.py
from .resources import *

# Import QgsMapCanvas Tool
from .selectionMapTool import initMapSelectTool

# Import the code for the dialog
from .OpenDataCube_Product_Loader_dialog import OpenDataCubeProductLoaderDialog
import os.path
from .load_layer import loadLayerDialog
from .psql_conn import psqlConnection
import os.path
import pandas as pd
import psycopg2

class OpenDataCubeProductLoader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OpenDataCubeProductLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dataDisplayDlg = OpenDataCubeProductLoaderDialog()
        self.loadLayerDialog = loadLayerDialog()
        self.loadLayerDialog.setModal(True)
        self.psqlConnectionDlg = psqlConnection()
        self.psqlConnectionDlg.setModal(True)
        self.dataDisplayDlg.lld = self.loadLayerDialog
        self.dataDisplayDlg.pConn = self.psqlConnectionDlg

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&OpenDataCube Product Loader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OpenDataCubeProductLoader')
        self.toolbar.setObjectName(u'OpenDataCubeProductLoader')

        # Set initial settings for dialogs
        self.dataDisplayDlg.mQgsFileWidget.setStorageMode(QgsFileWidget.GetDirectory)
        self.dataDisplayDlg.progressBar.setMinimum(0)
        self.dataDisplayDlg.progressBar.setValue(0)
        self.dataDisplayDlg.conDbServer.setCheckable(True)
        self.dataDisplayDlg.conDbServer.toggle()
        self.dataDisplayDlg.mQgsProjectionSelectionWidget.setOptionVisible(self.dataDisplayDlg.mQgsProjectionSelectionWidget.CrsNotSet,True)
        self.dataDisplayDlg.mQgsProjectionSelectionWidget.setNotSetText('Use default projection')

        # Create slots for dialog signals
        self.dataDisplayDlg.conDbServer.clicked.connect(lambda:self.dataDisplayDlg.checkDatabaseConnection(self.psqlConnectionDlg))
        self.psqlConnectionDlg.accepted.clicked.connect(lambda:self.dataDisplayDlg.createDatabaseConnection(self.psqlConnectionDlg))
        self.psqlConnectionDlg.ignored.clicked.connect(self.psqlConnectionDlg.close)
        self.dataDisplayDlg.plotData.clicked.connect(self.plotDatasets)
        self.dataDisplayDlg.datasetGeotiff.clicked.connect(self.array2raster)
        self.dataDisplayDlg.loadCoordinates.clicked.connect(self.loadLayerDialog.show)
        # self.dataDisplayDlg.helpButton.clicked.connect(self.)

        self.dataDisplayDlg.selectMapTool=initMapSelectTool(self.dataDisplayDlg.graphicsView)
        self.dataDisplayDlg.ingestedLayer=None
        self.dataDisplayDlg.graphicsView.setMapTool(self.dataDisplayDlg.selectMapTool)
        self.dataDisplayDlg.selectMapTool.featureIdentified.connect(self.dataDisplayDlg.loadCoordinatesInPlugin)

        self.loadLayerDialog.loadDefaultLayer.clicked.connect(lambda:self.loadLayerDialog.defaultLayer(self.iface,self.dataDisplayDlg.dbConnectionString,self.dataDisplayDlg))
        self.loadLayerDialog.loadUserLayer.clicked.connect(lambda:self.loadLayerDialog.userLayer(self.iface,self.dataDisplayDlg.dbConnectionString,self.dataDisplayDlg))

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OpenDataCubeProductLoader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/OpenDataCube_Product_Loader/assets/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'OpenDataCube Product Loader'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&OpenDataCube Product Loader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dataDisplayDlg.show()
        # Run the dialog event loop
        result = self.dataDisplayDlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def plotDatasets(self):
        from matplotlib import pyplot as py
        productList=self.dataDisplayDlg.listCheckedProducts()
        xMinMax=self.dataDisplayDlg.xMinMax.text()
        yMinMax=self.dataDisplayDlg.yMinMax.text()
        resolution=self.dataDisplayDlg.resText.text()
        startDate=self.dataDisplayDlg.startDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        endDate=self.dataDisplayDlg.endDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        column=self.dataDisplayDlg.colText.text()
        columnWrapText=int(self.dataDisplayDlg.colWrapText.text())

        if len(productList) is 0 or startDate is '' or endDate is '' or resolution is '':
            QMessageBox.information(None, "Warning:", str('Some required fields are missing. Please complete the form')) 
        elif startDate > endDate:
            QMessageBox.information(None, "Warning:", str('Start date cannot be more than end date.')) 

        elif startDate == endDate and column !='':
            QMessageBox.information(None, "Warning:", str('Please choose more than one dataframes to plot dataset by time')) 
        else:
            if xMinMax is '' or yMinMax is '':
                xMinMax=None
                yMinMax=None
            if column == '' or columnWrapText == '':
                column = None
                columnWrapText = None 
            if columnWrapText == 0:
                columnWrapText=None
            i=0
            dc=self.dataDisplayDlg.dc
            for keys in productList:
                try:
                    res1=float(resolution[:resolution.find(',')])
                    res2=float(resolution[resolution.find(',')+1:])
                    var=dc.load(product=keys,resolution=(res1,res2),time=(startDate,endDate), x=(xMinMax[:xMinMax.find(',')],xMinMax[xMinMax.find(',')+1:]),y=(yMinMax[:yMinMax.find(',')],yMinMax[yMinMax.find(',')+1:]))
                    #check if a matplot figure is already is plotted or not
                    if len(py.get_fignums()) > 0: 
                        py.close()
                    count=len(productList[keys])
                    for bands in productList[keys]:
                        
                        var.data_vars[bands].loc[startDate:endDate].plot(col=column,col_wrap=columnWrapText)
                        i = i + 1
                        percent = (i/float(count)) * 100
                        QApplication.processEvents() 
                        #setting the progress bar values
                        self.dataDisplayDlg.progressBar.setValue(percent)
                    py.show()
                    self.dataDisplayDlg.appendLogs('Data plotted successfully')
                except KeyError:
                    self.dataDisplayDlg.appendLogs('No dataset found for product:'+keys)
                    pass
                except (ValueError,RuntimeError,TypeError) as e:
                    self.dataDisplayDlg.appendLogs(e)
                    pass

    def loadRaster(self,raster):
        # Check if string is provided
        fileInfo = QFileInfo(raster)
        path = fileInfo.filePath()
        baseName = fileInfo.baseName()

        layer = QgsRasterLayer(path, baseName)
        QgsProject.instance().addMapLayer(layer)

        if layer.isValid() is True:
            self.dataDisplayDlg.appendLogs("Layer was loaded successfully!")
        else:
            self.dataDisplayDlg.appendLogs("Unable to read basename and file path - Your array is probably invalid")

    def array2raster(self):
        from osgeo import gdal, osr
        import re
        import numpy as np
        import os
        productList = self.dataDisplayDlg.listCheckedProducts() 
        resolution = self.dataDisplayDlg.resText.text()
        xMinMax = self.dataDisplayDlg.xMinMax.text()
        yMinMax = self.dataDisplayDlg.yMinMax.text()
        path = self.dataDisplayDlg.mQgsFileWidget.filePath()
        crs = self.dataDisplayDlg.mQgsProjectionSelectionWidget.crs()
        startDate = self.dataDisplayDlg.startDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        endDate = self.dataDisplayDlg.endDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        rasterOrigin = self.dataDisplayDlg.rasterOrigin.text()
        rasterOrigin = (rasterOrigin[:rasterOrigin.find(',')],rasterOrigin[rasterOrigin.find(',')+1:])
        selectCrs=self.dataDisplayDlg.mQgsProjectionSelectionWidget
        authId=selectCrs.crs().authid()
        if len(productList) == 0 or path == '' or startDate == '' or endDate == '':
            QMessageBox.information(None, "Warning:", str('Some required fields are missing. Please complete the form')) 
        elif startDate > endDate:
            QMessageBox.information(None, "Warning:", str('Start date cannot be greater than end date.')) 
        elif authId[:authId.find(':')] != 'EPSG' and authId != '':
            QMessageBox.information(None, "Warning:", str('Invalid CRS, please choose a valid EPSG CRS'))
        else:
            if xMinMax == '' or yMinMax == '':
                xMinMax = None
                yMinMax = None
            else:
                xMinMax = (float(xMinMax[:xMinMax.find(',')]),float(xMinMax[xMinMax.find(',')+1:]))
                yMinMax = (float(yMinMax[:yMinMax.find(',')]),float(yMinMax[yMinMax.find(',')+1:]))
            if resolution == '':
                resolution = None
            else:
                res1=float(resolution[:resolution.find(',')])
                res2=float(resolution[resolution.find(',')+1:])
                resolution=(res1,res2)
                time=(startDate,endDate)

            
            dc=self.dataDisplayDlg.dc
            dtypelist=dc.list_measurements().dtype.to_dict()
            self.dataDisplayDlg.progressBar.setValue(0)
            for keys in productList:
                try:
                    var=dc.load(product=keys,resolution=resolution, x=xMinMax,y=yMinMax,time=time)
                    if len(var) !=0:
                        timesets=var.time.data
                        i=0
                        count=len(productList[keys])*len(timesets)
                        rasterFolder=path+'\\'+keys+'-'+str(xMinMax[0])+','+str(xMinMax[1])+','+str(yMinMax[0])+','+str(yMinMax[1])
                        if authId == '':
                            crsId = self.extractEPSGCode(str(var.attrs['crs']))
                        else:
                            crsId = self.extractEPSGCode(authId) 
                        for times in timesets:
                            times=str(times)
                            for bands in productList[keys]:
                                dtype=dtypelist[(keys,bands)]

                                if not os.path.exists(rasterFolder):
                                    os.makedirs(rasterFolder)

                                newRasterfn =rasterFolder+'\\'+keys+'-'+bands+'-'+times.replace(':','').replace('-','')+'.tif'
                                array = np.array(var.data_vars[bands].loc[times:times])
                                array=array[0]
                                reversed_array=np.rot90(array,2)
                                cols = reversed_array.shape[1]
                                rows = reversed_array.shape[0]
                                originX = float(rasterOrigin[0])
                                originY = float(rasterOrigin[1])
                                driver = gdal.GetDriverByName('GTiff')
                                outRaster = driver.Create(newRasterfn, cols, rows, 1, self.GDTNumCode(dtype))
                                outRaster.SetGeoTransform((originX, resolution[0], 0, originY, 0, resolution[1]))
                                outband = outRaster.GetRasterBand(1)
                                outband.WriteArray(reversed_array)
                                outRasterSRS = osr.SpatialReference()
                                outRasterSRS.ImportFromEPSG(crsId)
                                outRaster.SetProjection(outRasterSRS.ExportToWkt())
                                # Exports the coordinate system 
                                outband.FlushCache()
                                del outband
                                del outRasterSRS
                                del outRaster
                                #deleting created objects
                                i = i + 1
                                percent = (i/float(count)) * 100
                                QApplication.processEvents()
                            #setting the progress bar values
                                self.dataDisplayDlg.progressBar.setValue(percent)
                                self.loadRaster(newRasterfn)
                    else:
                        raise IndexError
                except (KeyError,IndexError):
                    self.dataDisplayDlg.appendLogs('No dataset found for: '+keys)
                except RuntimeError as e:
                    self.dataDisplayDlg.appendLogs(e)

    def extractEPSGCode(self,authid):
        return int(authid[authid.find(':')+1:])

    def GDTNumCode(self,dtype):
        import numpy as np
        from osgeo import gdal, gdal_array
         
        typemap = {}
        for name in dir(np):
            obj = getattr(np, name)
            if hasattr(obj, 'dtype'):
                try:
                    npn = obj(0)
                    nat = np.asscalar(npn)
                    if gdal_array.NumericTypeCodeToGDALTypeCode(npn.dtype.type):
                        typemap[npn.dtype.name] = gdal_array.NumericTypeCodeToGDALTypeCode(npn.dtype.type)
                except:
                    pass 
        return typemap[dtype]
