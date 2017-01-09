# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI/settings.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_chatSettings(object):
    def setupUi(self, chatSettings):
        chatSettings.setObjectName("chatSettings")
        chatSettings.setWindowModality(QtCore.Qt.WindowModal)
        chatSettings.resize(230, 199)
        self.gridLayout = QtWidgets.QGridLayout(chatSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(chatSettings)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.settingsNick = QtWidgets.QLineEdit(chatSettings)
        self.settingsNick.setObjectName("settingsNick")
        self.verticalLayout.addWidget(self.settingsNick)
        self.label_2 = QtWidgets.QLabel(chatSettings)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.settingsServer = QtWidgets.QLineEdit(chatSettings)
        self.settingsServer.setObjectName("settingsServer")
        self.verticalLayout.addWidget(self.settingsServer)
        self.settingsOC = QtWidgets.QDialogButtonBox(chatSettings)
        self.settingsOC.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.settingsOC.setObjectName("settingsOC")
        self.verticalLayout.addWidget(self.settingsOC)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(chatSettings)
        QtCore.QMetaObject.connectSlotsByName(chatSettings)

    def retranslateUi(self, chatSettings):
        _translate = QtCore.QCoreApplication.translate
        chatSettings.setWindowTitle(_translate("chatSettings", "Settings"))
        self.label.setText(_translate("chatSettings", "Nickname"))
        self.label_2.setText(_translate("chatSettings", "Server (x.x.x.x:<port>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    chatSettings = QtWidgets.QDialog()
    ui = Ui_chatSettings()
    ui.setupUi(chatSettings)
    chatSettings.show()
    sys.exit(app.exec_())

