# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(963, 531)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.chatDisplay = QtWidgets.QTextEdit(self.centralwidget)
        self.chatDisplay.setAcceptDrops(False)
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setObjectName("chatDisplay")
        self.horizontalLayout_2.addWidget(self.chatDisplay)
        self.chatClients = QtWidgets.QListWidget(self.centralwidget)
        self.chatClients.setMaximumSize(QtCore.QSize(180, 16777215))
        self.chatClients.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.chatClients.setObjectName("chatClients")
        self.horizontalLayout_2.addWidget(self.chatClients)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.chatInput = QtWidgets.QLineEdit(self.centralwidget)
        self.chatInput.setObjectName("chatInput")
        self.verticalLayout_2.addWidget(self.chatInput)
        self.chatSend = QtWidgets.QPushButton(self.centralwidget)
        self.chatSend.setObjectName("chatSend")
        self.verticalLayout_2.addWidget(self.chatSend)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Chat Client"))
        self.chatSend.setText(_translate("MainWindow", "Send"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

