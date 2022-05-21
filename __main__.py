import sys
from PyQt5.QtWidgets import * 
from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3DWidget import QPanda3DWidget
from vtube import VTube

app = QApplication(sys.argv)
window = VTube()
window.show()
sys.exit(app.exec_())
