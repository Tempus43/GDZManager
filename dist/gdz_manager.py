from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QLabel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1313, 655)
        MainWindow.setMinimumSize(QtCore.QSize(1200, 300))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setContentsMargins(20, 10, 20, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())

        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(1000, 1000))
        self.scrollArea.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1000, 602))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(1000, 0))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setStyleSheet('QScrollArea { border: none; }')

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setContentsMargins(9, -1, 9, 6)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget.setMinimumSize(QtCore.QSize(970, 0))
        self.widget.setMaximumSize(QtCore.QSize(0, 16777215))
        self.widget.setObjectName("widget")

        self.horizontalLayout.addWidget(self.widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.addWidget(self.scrollArea)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1313, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.central_widget = QLabel(self)
        icon = QIcon('./gdz_icon.jpg')  # Путь к вашей иконке
        self.setWindowIcon(icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0.5)  # Устанавливаем прозрачность фона
        pixmap = QPixmap("./gdz_background.jpg")  # Путь к изображению
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
