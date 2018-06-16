from qgis.gui import QgsMapToolIdentifyFeature
class initMapSelectTool(QgsMapToolIdentifyFeature):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolIdentifyFeature.__init__(self, self.canvas)

    def keyPressEvent( self, e ):
        pass