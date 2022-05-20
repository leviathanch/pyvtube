import cv2
import mediapipe as mp
import numpy as np
import transforms3d
from mefamo.custom.face_geometry import (  # isort:skip
    PCF,
    get_metric_landmarks,
    procrustes_landmark_basis,
)

class OpenCVWorker:
	mp_face_mesh = mp.solutions.face_mesh
	face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5, refine_landmarks=True)
	mp_drawing = mp.solutions.drawing_utils
	mp_drawing_styles = mp.solutions.drawing_styles
	cap = None
	positions = {}
	parent = None
	smooth = {}
	points_idx = [33, 263, 61, 291, 199]
	orig_head_pos = None
	orig_right_eye_pos = (0,0)
	orig_left_eye_pos = (0,0)

	def __init__(self, parent):
		self.parent = parent
		self.points_idx = self.points_idx + [key for (key, val) in procrustes_landmark_basis]
		self.points_idx = list(set(self.points_idx))
		self.points_idx.sort()

	def startCapturing(self, videodev):
		if self.cap is None:
			self.cap = cv2.VideoCapture(0)

	def processImage(self, task):
		if self.cap is None:
			return task.cont
		if not self.cap.isOpened():
			return task.cont
		success, image = self.cap.read()
		if not success:
			return task.cont

		self.trackImage(image)

		return task.cont

	def stopCapturing(self):
		if self.cap is not None:
			self.cap.release()
			self.cap = None

		if self.parent is not None:
			self.parent.clearImage()

	def check_index(self, idx, l):
		for i in l:
			if(i[0]==idx):
				return True
		return False

	def get_fsval(self, l, i):
		idx=0
		for o in l:
			if(idx==i):
				return o
			idx+=1
		return (0,0)

	# Calculates the 3d rotation and 3d landmarks from the 2d landmarks
	def calculate_rotation(self, face_landmarks, pcf: PCF, image_shape):
		frame_width, frame_height, channels = image_shape
		focal_length = frame_width
		center = (frame_width / 2, frame_height / 2)
		camera_matrix = np.array(
			[[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
			dtype="double",
			)

		dist_coeff = np.zeros((4, 1))

		landmarks = np.array(
			[(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark[:468]]
			)
		landmarks = landmarks.T

		metric_landmarks, pose_transform_mat = get_metric_landmarks(
			landmarks.copy(), pcf
			)

		model_points = metric_landmarks[0:3, self.points_idx].T
		image_points = (
			landmarks[0:2, self.points_idx].T
			* np.array([frame_width, frame_height])[None, :]
			)

		success, rotation_vector, translation_vector = cv2.solvePnP(
			model_points,
			image_points,
			camera_matrix,
			dist_coeff,
			flags=cv2.SOLVEPNP_ITERATIVE,
		)

		return pose_transform_mat, metric_landmarks, rotation_vector, translation_vector

	# Keeps a moving average of given length
	def smooth_value(self, name, length, value):
		if not name in self.smooth:
			self.smooth[name] = np.array([value])
		else:
			self.smooth[name] = np.insert(arr=self.smooth[name], obj=0, values=value)
			if self.smooth[name].size > length:
				self.smooth[name] = np.delete(self.smooth[name], self.smooth[name].size-1, 0)
		sum = 0
		for val in self.smooth[name]:
			sum += val
		return sum / self.smooth[name].size

	def trackImage(self, image):
		# Flip the image horizontally for a later selfie-view display
		# Also convert the color space from BGR to RGB
		#image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

		# To improve performance
		image.flags.writeable = False
		
		# Get the result
		results = self.face_mesh.process(image)
		
		# To improve performance
		image.flags.writeable = True
		
		# Convert the color space from RGB to BGR
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		img_h, img_w, img_c = image.shape

		# The camera matrix
		focal_length = 1 * img_w
		self.camera_matrix = np.array([ [focal_length, 0, img_h / 2],
			[0, focal_length, img_w / 2],
			[0, 0, 1]])

		self.pcf = PCF(
            near=1,
            far=10000,
            frame_height=img_w,
            frame_width=img_h,
            fy=self.camera_matrix[1, 1],
        )

		if results.multi_face_landmarks:
			for face_landmarks in results.multi_face_landmarks:
				right_eye_pos = [0, 0]
				left_eye_pos = [0, 0]
				for idx, lm in enumerate(face_landmarks.landmark):
					if self.check_index(idx, self.mp_face_mesh.FACEMESH_LIPS):
						if idx==17: # lower lip
							x, y = int(lm.x * img_w), int(lm.y * img_h)
							cv2.circle(image, (x, y), 10, (0, 0, 255), 1)
						elif idx==61: # left side of mouth
							x, y = int(lm.x * img_w), int(lm.y * img_h)
							cv2.circle(image, (x, y), 10, (0, 255, 0), 1)
						elif idx==409: # right side of mouth
							x, y = int(lm.x * img_w), int(lm.y * img_h)
							cv2.circle(image, (x, y), 10, (255, 0, 0), 1)
						elif idx==0: # upper lip 
							x, y = int(lm.x * img_w), int(lm.y * img_h)
							cv2.circle(image, (x, y), 10, (255, 55, 0), 1)
					elif self.check_index(idx, self.mp_face_mesh.FACEMESH_RIGHT_IRIS):
						x, y = int(lm.x * img_w), int(lm.y * img_h)
						right_eye_pos[0] = right_eye_pos[0] + x
						right_eye_pos[1] = right_eye_pos[1] + y
					elif self.check_index(idx, self.mp_face_mesh.FACEMESH_LEFT_IRIS):
						x, y = int(lm.x * img_w), int(lm.y * img_h)
						left_eye_pos[0] = left_eye_pos[0] + x
						left_eye_pos[1] = left_eye_pos[1] + y

				cv2.circle(image, (int(right_eye_pos[0]/4), int(right_eye_pos[1]/4)), 4, (0, 255, 255), 1)
				cv2.circle(image, (int(left_eye_pos[0]/4), int(left_eye_pos[1]/4)), 4, (0, 255, 255), 1)

				# the HPR vector for the head
				pose_transform_mat, metric_landmarks, rotation_vector, translation_vector = self.calculate_rotation(face_landmarks, self.pcf, image.shape)
				eulerAngles = transforms3d.euler.mat2euler(pose_transform_mat)
				h=self.smooth_value("head_h", 5, eulerAngles[1]*57)
				p=self.smooth_value("head_p", 5, -eulerAngles[0]*57)
				r=self.smooth_value("head_r", 5, eulerAngles[2]*57)
				self.positions['head_hpr'] = (h, p, r)

				if self.orig_head_pos is None:
					self.orig_head_pos = translation_vector
					self.positions['head_pos'] = (0,0,0) 
				else:
					self.positions['head_pos'] = translation_vector - self.orig_head_pos

				self.mp_drawing.draw_landmarks(
					image,
					landmark_list=face_landmarks,
					connections=self.mp_face_mesh.FACEMESH_TESSELATION,
					landmark_drawing_spec=None,
					connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
					)
				self.mp_drawing.draw_landmarks(
					image,
					landmark_list=face_landmarks,
					connections=self.mp_face_mesh.FACEMESH_CONTOURS,
					landmark_drawing_spec=None,
					connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
					)
	
				if self.parent is not None:
					self.parent.displayImage(image)
					self.parent.updatePositions(self.positions)

	def calculateHeadHPR(self, image):
		return (h, p, r)
