# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ontheway
                                 A QGIS plugin
 Calculate route
                              -------------------
        begin                : 2016-08-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Adam Borczyk
        email                : ad.borczyk@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ontheway_dialog import onthewayDialog
import os.path
## Additional resources
from qgis.core import QgsPoint, QgsMapLayerRegistry, QgsGeometry, QgsVectorLayer, QgsField, QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.gui import QgsMessageBar
import urllib, json
from utils import *
from config import YOUR_API_KEY


class ontheway:
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

        ## To get EPSG from canvas
        canvas = self.iface.mapCanvas() 
        self.currentEPSG = canvas.mapRenderer().destinationCrs().authid()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ontheway_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference, window on top
        self.dlg = onthewayDialog(self.iface.mainWindow())

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&onTheWay')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ontheway')
        self.toolbar.setObjectName(u'ontheway')

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
        return QCoreApplication.translate('ontheway', message)


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

        icon_path = ':/plugins/ontheway/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Get route'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&onTheWay'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def zipToCoords(self, code):
        """ Get centroid of postal code and return it's coordinates """
        ## Get original geometry
        queryString = 'http://127.0.0.1:5000/%s' % code
        response = urllib.urlopen(queryString)
        data = json.loads(response.read())
        if data != code: ## if code exists in database
            count = 0
            ## Create dict of geometry of postal code area...
            tempPolygons = []
            for j in data['coordinates']:    
                tempPoints = [QgsPoint(i[0], i[1]) for i in data['coordinates'][count][0]]
                count += 1
                tempPolygons.append([tempPoints])        
            ## ... and store it in MultiPolygon geometry
            geom = QgsGeometry.fromMultiPolygon(tempPolygons).centroid()     

            ## Transform CRS to 4326 desired by Skobbler
            crsSrc = QgsCoordinateReferenceSystem(2180) ## database CRS
            crsDest = QgsCoordinateReferenceSystem(4326) ## WGS-84
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            geom.transform(xform)
            return str(geom.asPoint().y())+','+str(geom.asPoint().x())
        else:    
            return 'keyerror'

    def requestRoute(self):
        """ Send the Route request """
        ## Get the data
        response = urllib.urlopen(url_routing % (self.zipToCoords(self.dlg.lineEdit_1.text()), 
                                                self.zipToCoords(self.dlg.lineEdit_2.text()),
                                                self.highways,
                                                self.toll))
        
        data = json.loads(response.read())
        try:
            return data['route']['routePoints']
        except KeyError:
            return 'keyerror'

    def requestReach(self, url_distance, url_units):
        """ Send the Reach requests """
        ## Get the data
        tempStarts = self.createRoute()
        if tempStarts != 'keyerror':
            datasets = []
            ## Get reach for each node in the route
            for item in tempStarts[:10]: ### simplified to first 10 nodes only, creates approx. 30 km per 1 minute
                response = urllib.urlopen(url_realreach % (item, url_distance, url_units, self.highways, self.toll))
                data = json.loads(response.read())
                try:
                    datasets.append(data['realReach']['gpsPoints'])
                except KeyError:
                    return 'keyerror'
            return datasets
        else:
            return 'keyerror'

    def createRoute(self):
        """ Create shapefile from returned list of points """
        vl = QgsVectorLayer("linestring?crs=EPSG:4326", 'Route', "memory")
        pr = vl.dataProvider()

        ## Add feature name in attribute table
        pr.addAttributes([QgsField("route", QVariant.String)])
        vl.updateFields()

        ## Load coordinates of nodes from routing
        coords = self.requestRoute()
        if coords != 'keyerror':
            points = [] 
            for item in coords:
                points.append(QgsPoint(item['x'],item['y']))

            ## Prepare starting points for RealReach        
            self.tempStarts = []
            for i in range(0,len(coords)):
                tempStart = str(coords[i]['y'])+','+str(coords[i]['x'])
                self.tempStarts.append(tempStart)      

            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPolyline(points))

            ## Set feature name/attribute
            fet.setAttributes(["Route "+self.dlg.lineEdit_1.text()+" - "+self.dlg.lineEdit_2.text()])
            pr.addFeatures([fet])

            ## Add prepared layer with transparency
            vl.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayer(vl)

            return self.tempStarts
        else:
            return 'keyerror'

    def createReach(self):
        """ Create shapefile from returned list of points """
        ## Create one layer for multiple polygons and one for single combined polygon that will be displayed
        vl = QgsVectorLayer("Polygon?crs=EPSG:4326", "tempVectorLayer", "memory")
        vl_combine = QgsVectorLayer("Polygon?crs=EPSG:4326", "Reach", "memory")
        pr = vl.dataProvider()
        pr_combine = vl_combine.dataProvider()

        ## Add feature name in attribute table
        pr.addAttributes([QgsField("tempField", QVariant.String)])
        vl.updateFields()
        pr_combine.addAttributes([QgsField("source", QVariant.String), 
                                QgsField("dest", QVariant.String), 
                                QgsField("range", QVariant.Int),
                                QgsField("unit", QVariant.String),
                                QgsField("highways", QVariant.Int),
                                QgsField("toll", QVariant.Int)])
        vl_combine.updateFields()

        ## Create parameters for RealReach URL to be requested
        distance = self.dlg.spinBox.value()*1000 if self.dlg.radioButton_1.isChecked() else self.dlg.spinBox.value()*60
        units = 'meter' if self.dlg.radioButton_1.isChecked() else 'sec'
        self.highways = '1' if self.dlg.checkBox_1.checkState() else '0'
        self.toll = '1' if self.dlg.checkBox_2.checkState() else '0'

        datasets = self.requestReach(distance, units)

        if datasets != 'keyerror':
            for item in datasets:
                ## Create geometry from points
                points = []
                x = [item[i] for i in range(1, len(item), 2)]
                y = [item[i] for i in range(0, len(item), 2)]
                
                for i, j in zip(y[4:], x[4:]):
                    points.append(QgsPoint(i,j))

                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolygon([points]))

                ## Set feature name/attribute
                fet.setAttributes(["temp"])
                pr.addFeatures([fet])

            ## Create new geometry for single polygon
            newGeometry = QgsGeometry.fromWkt('GEOMETRYCOLLECTION EMPTY')

            for feature in vl.getFeatures():
                newGeometry = newGeometry.combine(feature.geometry())

            fet_combine = QgsFeature()
            fet_combine.setGeometry(QgsGeometry.fromPolygon(newGeometry.asPolygon())) 

            ## Fill attribute table
            fet_combine.setAttributes([self.dlg.lineEdit_1.text(),
                                    self.dlg.lineEdit_2.text(),
                                    self.dlg.spinBox.value(),
                                    ('kilometers' if self.dlg.radioButton_1.isChecked() else 'minutes'),
                                    (1 if self.dlg.checkBox_1.checkState() else 0),
                                    (1 if self.dlg.checkBox_2.checkState() else 0)])
            pr_combine.addFeatures([fet_combine])          

            ## Add prepared layer with transparency
            vl_combine.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayer(vl_combine)
            vl_combine.setLayerTransparency(50)
        else:
            return 'keyerror'

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            output = self.createReach()
            if output == 'keyerror':
                self.iface.messageBar().pushMessage("Error", "Jeden lub oba kody sa nieprawidlowe", level=QgsMessageBar.WARNING, duration=3)