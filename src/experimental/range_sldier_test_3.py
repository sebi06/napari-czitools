from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Sliders(object):
    def setupUi(self, Sliders):
        Sliders.setObjectName("Sliders")
        Sliders.resize(259, 203)
        self.verticalLayout = QtWidgets.QVBoxLayout(Sliders)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Slider1 = QtWidgets.QSlider(Sliders)
        self.Slider1.setMinimumSize(QtCore.QSize(241, 16))
        self.Slider1.setOrientation(QtCore.Qt.Horizontal)
        self.Slider1.setObjectName("Slider1")
        self.verticalLayout.addWidget(self.Slider1)
        self.Slider2 = QtWidgets.QSlider(Sliders)
        self.Slider2.setMinimumSize(QtCore.QSize(241, 16))
        self.Slider2.setOrientation(QtCore.Qt.Horizontal)
        self.Slider2.setObjectName("Slider2")
        self.verticalLayout.addWidget(self.Slider2)
        spacerItem = QtWidgets.QSpacerItem(20, 108, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(Sliders)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Sliders)
        self.buttonBox.accepted.connect(Sliders.accept)
        self.buttonBox.rejected.connect(Sliders.reject)
        QtCore.QMetaObject.connectSlotsByName(Sliders)

    def retranslateUi(self, Sliders):
        _translate = QtCore.QCoreApplication.translate
        Sliders.setWindowTitle(_translate("Sliders", "Dialog"))

    def Slider1SetValue(self, _v):
        self.Slider1.setValue(99 - _v)

    def Slider2SetValue(self, _v):
        self.Slider2.setValue(99 - _v)


# ==============================================================================
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Sliders = QtWidgets.QDialog()
    ui = Ui_Sliders()
    ui.setupUi(Sliders)
    ui.Slider1.setValue(99)
    ui.Slider2.setValue(0)
    ui.Slider1.valueChanged.connect(ui.Slider2SetValue)
    ui.Slider2.valueChanged.connect(ui.Slider1SetValue)
    Sliders.show()
    sys.exit(app.exec_())
