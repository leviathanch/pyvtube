from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys

class CoordinatePanel(QDockWidget):
	def __init__(self, parent=None):
		super(CoordinatePanel, self).__init__(parent)
		self.setWindowTitle('Facial points')
		self.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
		self.setMinimumSize(200,200)

		layout = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(layout)
		self.setWidget(widget)

		# create coordinate sheet
		title = QLabel()
		title.setText("Head HPR:")
		title.setStyleSheet("font-weight: bold;");
		layout.addWidget(title)

		self.head_hpr = QLabel()
		self.head_hpr.setText("(0,0,0)")
		layout.addWidget(self.head_hpr)

	def updatePositions(self, positions):
		self.head_hpr.setText(str(positions["head_hpr"]))
