from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout
import sys
import numpy as np
import re
from transport import traffic, nwa


WIDTH = 1200
HEIGHT = 900


class LabelGrid(QtWidgets.QWidget):
    def __init__(self, parent, size_x, size_y):
        super(LabelGrid, self).__init__(parent)
        self.size_x = size_x
        self.size_y = size_y
        self.labels = []
        grid_layout = QtWidgets.QGridLayout()
        self.setLayout(grid_layout)
        for i in range(self.size_y):
            self.labels.append([])
            for j in range(self.size_x):
                label = QtWidgets.QLabel()
                self.labels[i].append(label)
                grid_layout.addWidget(label, i, j)

    def set_value(self, values):
        for i in range(self.size_y):
            for j in range(self.size_x):
                self.labels[i][j].setText(str(values[i, j]))


class InputGrid(QtWidgets.QWidget):
    def __init__(self, parent, size_x, size_y):
        super(InputGrid, self).__init__(parent)
        self.size_x = size_x
        self.cap_x = size_x
        self.size_y = size_y
        self.cap_y = size_y
        self.entries = []
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        for i in range(self.size_y):
            self.entries.append([])
            for j in range(self.size_x):
                entry = QtWidgets.QLineEdit()
                self.entries[i].append(entry)
                self.layout.addWidget(entry, i, j)


    def get_value(self):
        res = []
        for i in range(self.size_y):
            res.append([])
            for j in range(self.size_x):
                tmp = self.entries[i][j].text()
                if tmp and re.match(r'\d+\.*\d*', tmp):
                    res[i].append(float(tmp))
                else:
                    res[i].append(0.0)
        return np.array(res)






class Ui_MainWindow(QtWidgets.QWidget):
    def setupUi(self, MainWindow):
        MainWindow.resize(WIDTH, HEIGHT)
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(700, 400, 200, 100))
        self.cost_inputGrid = InputGrid(self.centralwidget, 5, 4)
        self.production_inputGrid = InputGrid(self.centralwidget, 1, 4)
        self.consumption_inputGrid = InputGrid(self.centralwidget, 5, 1)
        self.outputGrid = LabelGrid(self.centralwidget, 5, 4)
        self.cost_inputGrid.setGeometry(QtCore.QRect(10, 10, 600, 300))
        self.production_inputGrid.setGeometry(QtCore.QRect(650, 10, 135, 300))
        self.consumption_inputGrid.setGeometry(QtCore.QRect(10, 350, 600, 100))
        self.outputGrid.setGeometry(QtCore.QRect(25, 450, 600, 300))
        self.invalid_input_label = QLabel(self.centralwidget)
        self.invalid_input_label.setGeometry(QtCore.QRect(10, 450, 500, 50))
        self.invalid_input_label.setText('Invalid_input')
        self.invalid_input_label.hide()
        self.error_label = QLabel(self.centralwidget)
        self.error_label.setText('Error: sum of production should\n'
                                    +'be equal to sum of consumtion')
        self.error_label.hide()
        self.error_label.setGeometry(QtCore.QRect(30, 500, 500, 100))
        self.price_label = QLabel(self.centralwidget)
        self.price_label.setGeometry(QtCore.QRect(25, 730, 500, 100))
        self.price_label.hide()

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Proceed"))
        self.pushButton.clicked.connect(self.perform)

    def perform(self):
        c = self.cost_inputGrid.get_value()
        a = self.production_inputGrid.get_value()[:, 0]
        b = self.consumption_inputGrid.get_value()[0]
        self.error_label.hide()
        if np.sum(np.sum(a) == np.sum(b)):
            self.outputGrid.show()
            self.price_label.show()
            d, is_base = nwa(c, a, b)
            d, is_base, p = traffic(c, d, is_base)
            while p.any():
                d, is_base, p = traffic(c, d, is_base)
            d = np.round(d, 5)
            self.outputGrid.set_value(d)
            self.price_label.setText('Ціна транспортування: ' + str(np.sum(d*c)))
            self.price_label.show()
        else:
            self.price_label.hide()
            self.outputGrid.hide()
            self.error_label.show()
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show() 

    sys.exit(app.exec_())
