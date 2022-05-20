import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ControlPanel(QDockWidget):
	# the tracker object
	cvworker = None

	def __init__(self, parent=None):
		super(ControlPanel, self).__init__(parent)
		self.setWindowTitle('VTube Control Panel')
		self.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
		self.setMinimumSize(200,200)

		layout = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(layout)
		self.setWidget(widget)

		# TODO make camera name configurable here:
		self.videoname = "/dev/video0"
		
		self.startButton = QPushButton("Start capture")
		self.startButton.clicked.connect(self.startCapture)
		icon = self.style().standardIcon(QStyle.SP_MediaPlay)
		self.startButton.setIcon(icon)
		layout.addWidget(self.startButton)

		self.stopButton = QPushButton("Stop capture")
		self.stopButton.clicked.connect(self.stopCapture)
		icon = self.style().standardIcon(QStyle.SP_MediaStop)
		self.stopButton.setIcon(icon)
		layout.addWidget(self.stopButton)

		self.startButton.setEnabled(False)
		self.stopButton.setEnabled(False)

	def setWorker(self, worker):
		self.cvworker = worker
		self.startButton.setEnabled(True)

	def startCapture(self):
		if self.cvworker is not None:
			self.cvworker.startCapturing(self.videoname)
			self.startButton.setEnabled(False)
			self.stopButton.setEnabled(True)

	def stopCapture(self):
		if self.cvworker is not None:
			self.cvworker.stopCapturing()
			self.startButton.setEnabled(True)
			self.stopButton.setEnabled(False)
