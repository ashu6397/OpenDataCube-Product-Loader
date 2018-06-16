# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dataDisplayDialog
                                 A QGIS plugin
 This plugin displays data from datacube
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-05-06
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Ashu
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

import os
from PyQt5 import uic
from PyQt5 import QtWidgets
import qgis
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt,pyqtSlot
from PyQt5.QtWidgets import QAction,QMessageBox,QTreeWidget,QTreeWidgetItem

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'OpenDataCube_Product_Loader_dialog_base.ui'))
import time
import psycopg2
import datacube

class OpenDataCubeProductLoaderDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(OpenDataCubeProductLoaderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.dbConnectionString=None
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def closeEvent(self,event):
        reply=QtWidgets.QMessageBox.question(self,'OpenDatacube',"Are you sure to quit?",QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        if reply==QtWidgets.QMessageBox.Yes:
            event.accept()
            qgis.utils.reloadPlugin('opendatacubeproductloader')
            self.pConn.close()
            self.lld.close()
            if self.dbConnectionString is not None: 
                self.dbConnectionString.close()
        else:
            event.ignore()

    def appendLogs(self,text):
        self.displayLogs.setReadOnly(True)
        self.displayLogs.textCursor().insertHtml(time.strftime('%m/%d/%Y %I:%M:%S %p')+'&nbsp;'+str(text)+'<br>')

    #list products and their variables to let the user choose
    def listProducts(self): 
        global dc
        try:
            dc=datacube.Datacube(app="dc")
            product_name=dc.list_products().name.tolist()
            if len(product_name) != 0:
                product_variables=[]
                for products_variables in dc.list_measurements().name.to_dict():
                    product_variables.append(products_variables)
                for products in product_name:
                    #create a tree item
                    parent=QTreeWidgetItem(self.treeProductInfo) 
                    #add parent item
                    parent.setText(0,products) 
                    #set flag of tristate checkbox
                    parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable) 
                    #extract band variables from product variable list
                    for product_vars,var in product_variables: 
                        if product_vars == products:
                            #add child to the parent item 
                            child=QTreeWidgetItem(parent) 
                            #set the checkbox flag user checkable
                            child.setFlags(child.flags() | Qt.ItemIsUserCheckable) 
                            child.setText(0,var) 
                            child.setCheckState(0, Qt.Unchecked)
                            #to display products in tree view 
                    self.treeProductInfo.addTopLevelItem(parent) 
                self.appendLogs('Products loaded!')
            else:
                self.appendLogs('Product List Empty!')
        except datacube.index.postgres._connections.IndexSetupError:
            self.appendLogs('No DB schema exists. Have you run init? datacube system init')

    def showIngestedDataProductList(self):
        import ast
        import datetime        
        try:
            curs=self.dbConnectionString.cursor()
            product_name=dc.list_products().name.tolist()
            if len(product_name) != 0:
                product_variables=[]
                for products_variables in dc.list_measurements().name.to_dict():
                    product_variables.append(products_variables)
                for products in product_name:
                    parent=QTreeWidgetItem(self.treeProductInfo_2) #create a tree item
                    parent.setText(0,products) #add parent item
                    dataset_info_dict={}
                    curs.execute('SELECT id,lat,lon,upper(time) FROM agdc.dv_'+products+'_dataset;')
                    for info in curs:
                        i=str(ast.literal_eval(info[1])+ast.literal_eval(info[2]))
                        dataset_info_dict[i]=dataset_info_dict.get(i,())
                        dataset_info_dict[i]+=(info[0],info[3].strftime('%d-%m-%Y'))
                    for keys in dataset_info_dict:
                        child=QTreeWidgetItem(parent) #create a tree item
                        child.setText(0,keys) #add parent item
                        for values in dataset_info_dict[keys]:
                            child1=QTreeWidgetItem(child) #create a tree item
                            child1.setText(0,values) #add parent item
                    self.treeProductInfo_2.addTopLevelItem(parent) #to display products in tree view 
            self.dc=dc
        except datacube.index.postgres._connections.IndexSetupError:
            self.appendLogs('No DB schema exists. Have you run init? datacube system init')

    def checkDatabaseConnection(self,dialog):
        if self.conDbServer.isChecked() and self.dbConnectionString != None:
            self.conDbServer.setText('Connect Database Server')
            self.dbConnectionString.close()
            self.treeProductInfo.clear()
            self.treeProductInfo_2.clear()
            self.appendLogs('Database Connection Closed')
        else:
            dialog.show()

    def createDatabaseConnection(self,dialog):
        host=dialog.hostText.text()
        port=dialog.portText.text()
        username=dialog.userText.text()
        password=dialog.passText.text()
        database=dialog.dbText.text()   
        try:
            if host is '' or port is '' or username is '' or database is '':
                QMessageBox.information(None, "Warning:", str('Some required fields are missing. Please complete the form'))  
            else:
                self.dbConnectionString=psycopg2.connect(database=database, user=username, password=password, host=host, port=port)
                self.appendLogs(self.dbConnectionString.dsn)
                self.conDbServer.setText('Disconnect Database Server')
                self.listProducts()
                self.showIngestedDataProductList()
                dialog.close()
        except psycopg2.Error as e:
            self.dbConnectionString=None
            self.appendLogs(e)  

    def listCheckedProducts(self):
        checked = dict()
        root = self.treeProductInfo.invisibleRootItem()
        signal_count = root.childCount()

        for i in range(signal_count):
            signal = root.child(i)
            checked_sweeps = list()
            num_children = signal.childCount()

            for n in range(num_children):
                child = signal.child(n)

                if child.checkState(0) == Qt.Checked:
                    checked_sweeps.append(child.text(0))
            if signal.checkState(0) == Qt.Checked:
                checked[signal.text(0)] = checked_sweeps
            elif signal.checkState(0) == Qt.PartiallyChecked:
                checked[signal.text(0)] = checked_sweeps

        return checked

    def loadCoordinatesInPlugin(self,feature):
        self.ingestedLayer.removeSelection()
        self.ingestedLayer.select(feature.id())
        self.xMinMax.setText(','.join(feature['extent'].split(",", 2)[:2]))
        self.yMinMax.setText(','.join(feature['extent'].split(",", 2)[2:]))