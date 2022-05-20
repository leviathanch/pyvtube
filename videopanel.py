import sys

import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class VideoPanel(QDockWidget):
	cvimage = None
	def __init__(self, parent=None):
		super(VideoPanel, self).__init__(parent)
		self.setWindowTitle('OpenCV')
		self.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
		self.setMinimumSize(1000,1000)

		layout = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(layout)
		self.setWidget(widget)

		self.cvimage = QLabel(self)
		layout.addWidget(self.cvimage)

	def displayImage(self, image):
		img = self.convertCV2QT(image)
		self.cvimage.setPixmap(img)

	def clearImage(self):
		self.cvimage.clear()

	def convertCV2QT(self, cv_img):
		"""Convert from an opencv image to QPixmap"""
		rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
		h, w, ch = rgb_image.shape
		bytes_per_line = ch * w
		convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
		p = convert_to_Qt_format.scaled(self.width()*0.95, self.height()*0.95, Qt.KeepAspectRatio)
		return QPixmap.fromImage(p)
