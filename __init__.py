import sys

# Qt Panda3d
from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3DWidget import QPanda3DWidget

# Panda3D stuff
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectFrame

from direct.actor.Actor import Actor
from panda3d.core import * 

# Qt 5 stuff
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from PyQt5.QtCore import Qt

from vtube.controlpanel import ControlPanel
from vtube.videopanel import VideoPanel
from vtube.coordinatepanel import CoordinatePanel
from vtube.facerecognition import OpenCVWorker 

class VTubePanda(Panda3DWorld):
	orig_head_hpr = None
	orig_head_pos = None
	joints = {}

	def __init__(self):
		Panda3DWorld.__init__(self)
		self.cam.setPos(0, 0, 0)
		self.win.setClearColorActive(True)
		self.win.setClearColor(VBase4(0, 0.5, 0, 1))
		self.scene = self.loader.loadModel("scene")
		self.scene.reparentTo(render)
		self.scene.setScale(1, 1, 1)
		self.scene.setPos(0, 0, 0)
		self.loadAvatar()

	def loadAvatar(self):
		self.pandaActor = Actor('snaky.egg')
		self.pandaActor.setPos((0, 10, 1))
		dlight = DirectionalLight('my dlight')
		dlnp = render.attachNewNode(dlight)
		self.pandaActor.setLight(dlnp)

		self.pandaActor.reparentTo(render)
		print(self.pandaActor.getJoints())

		self.rootJoint = self.pandaActor.controlJoint(None, "modelRoot", "Root") # The root of the model

		self.headJoint = self.pandaActor.controlJoint(None, "modelRoot", "Head")
		self.headJoint.reparentTo(self.rootJoint)

		self.jawJoint = self.pandaActor.controlJoint(None, "modelRoot", "Jaw")
		self.jawJoint.reparentTo(self.headJoint)

		self.snoutJoint = self.pandaActor.controlJoint(None, "modelRoot", "Snout")
		self.snoutJoint.reparentTo(self.headJoint)

		self.leftUpperTooth = self.pandaActor.controlJoint(None, "modelRoot", "Left Upper tooth")
		self.leftUpperTooth.reparentTo(self.headJoint)

		# Left eye, Left eyeball
		#Left Lower Lip 3, Left Lower Lip 2, Left Lower Lip 1, 

		print(self.headJoint.getChildren())

	def setWorker(self, worker):
		print("Setting worker")
		self.updateTask = taskMgr.add(worker.processImage, "update")

	def updatePositions(self, positions):
		if self.orig_head_hpr is None: # first run
			self.orig_head_hpr = self.headJoint.getHpr()
		hpr = self.orig_head_hpr + LVecBase3f(positions["head_hpr"][0], positions["head_hpr"][1], positions["head_hpr"][2])
		self.headJoint.setHpr(hpr)

		#if self.orig_head_pos is None: # first run
		#	self.orig_head_pos = self.headJoint.getPos()
		#pos = self.orig_head_pos + LVecBase3f(positions["head_pos"][0], positions["head_pos"][1], positions["head_pos"][2])
		#self.headJoint.setPos(pos)

class VTube(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle('PyVTube')
		self.setGeometry(0, 0, 1000, 1000)
		self.world = VTubePanda()
		pandaWidget = QPanda3DWidget(self.world)
		self.setCentralWidget(pandaWidget)

		self.cvworker = OpenCVWorker(self)
		self.world.setWorker(self.cvworker)

		self.control = ControlPanel(self)
		self.control.setWorker(self.cvworker)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.control)

		self.coords = CoordinatePanel(self)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.coords)

		self.video = VideoPanel(self)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.video)

	def displayImage(self, image):
		self.video.displayImage(image)

	def clearImage(self):
		self.video.clearImage()

	def updatePositions(self, positions):
		self.world.updatePositions(positions)
		self.coords.updatePositions(positions)


