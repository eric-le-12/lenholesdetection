"""
This class is utilized to detect holes with lens and no lens in an image
Log:
27/6/2019: Update select_roi package
25/6/2019: First Created
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from skimage.morphology import disk
from keras.models import load_model


class LenDetection():
	"""
	This class is utilized to detect len holes and holes without any len!
	"""

	def __init__(self,image_path,
				output_path,
				min_radius=10,
				average_top_k_radius=None):
		"""Initilize function
		Arguments:
			image_path {[str]} -- [path to image]
			output_path {[str]} -- [path to location of folder to save output images]
			min_radius {[int]} -- [minimum radius of a hole to rule out small holes]

		Keyword Arguments:
			average_top_k_radius {[int/None]} -- [finding radius by average k most frequent radius] (default: {None})
		"""
		self.image_path=image_path
		self.output_path=output_path
		self.top_k_radius=average_top_k_radius
		self.min_radius=min_radius
		self.width=980  # displaying resolution
		self.height=980  # displaying resolution

	def select_roi(self):
		"""Select Region of Interest
		Returns:
			starting_point[list] -- [coordinates x and y of top-left point of the ROI]
			roi_image            -- [ROI image]
		"""
		# create a window with predifined width and size, read input
		cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)
		image=cv2.imread(self.image_path)
		cv2.resizeWindow('Original Image', self.width,self.height)
		# Select ROI
		roi = cv2.selectROI('Original Image',image)
		# Crop image
		roi_image = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
		# Display cropped image
		cv2.namedWindow('Region of Interest', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Region of Interest', self.width, self.height)
		cv2.imshow('Region of Interest', roi_image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		starting_point=[roi[0],roi[1]]
		cv2.imwrite('roi.jpg',roi_image)
		return starting_point,roi_image
		
	def extract_binary_image(self):
		# this function used to extract binary image, return a binary image
		# extract grayscale image from ROI
		roi_image=cv2.imread('roi.jpg')
		gray=cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
		# filter the image with Gaussian blur
		gray = cv2.GaussianBlur(gray, (3, 3), 2, 2)
		# perform histogram equalization
		gray=cv2.equalizeHist(gray)
		binary=cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 12)
		binary_image=binary
		return binary_image
		
	def finding_radius(self,binary_image):
		# finding possible radius for holes
		# finding all contour
		[im2, contours, hierarchy] = cv2.findContours(binary_image,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
		# finding all radius
		min_radius=self.min_radius
		r=[]
		# loop all contours and find their radii
		for i,c in enumerate(contours):
			peri = cv2.arcLength(c, True)
			area = cv2.contourArea(c,True)
			r.append(np.round(np.sqrt(area/3.14)))
		r=pd.Series(r)
		r=r[r>min_radius]
		if self.top_k_radius is not None:
			det_r=r.value_counts().head(int(top_k_radius))
			det_r=pd.Series(det_r.index).sum()/int(top_k_radius)
		else:
			det_r=r.value_counts().head(1)
			det_r=det_r.idxmax()
		det_r=int(det_r)
		print('radius found: %d ',det_r)
		return det_r
		
	def circle_len_detection(self,det_r,binary_image,roi_image):
		# detect circular holes, return centroid of that holes
		[im2, contours, hierarchy] = cv2.findContours(binary_image,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
		# create a list to save centroid coordinate
		centroid=[]
		im=roi_image
		model = load_model('model_final.h5')
		for i,c in enumerate(contours):
			# approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.015 * peri, True)
			area = cv2.contourArea(c,True)
	
			# if our approximated contour has 9 points, area>= minimum area then
			# we can assume that we have found our circular holes
			if ((len(approx) >= 9) and (hierarchy[0,i,2]==-1) and area>3.14*self.min_radius*self.min_radius):
				# find moments and centroid: cX,cY
				moment=cv2.moments(c)
				cX=int(moment["m10"] / moment["m00"])
				cY=int(moment["m01"] / moment["m00"])
				# extract the current contour into a new variable, then predict
				window=im[cY-det_r:cY+det_r,cX-det_r:cX+det_r]
				window=cv2.cvtColor(window, cv2.COLOR_BGR2RGB)
				window=cv2.resize(window,(48,48))
				windowrs=window.reshape(1,48,48,3)
				prediction=model.predict(windowrs)
				if(np.max(prediction)<0.5):
					continue
				# get label of classification and draw circle
				label=int((prediction).argmax(axis=-1))
				cv2.circle(roi_image,(cX,cY),det_r,(0,255*label,255*(1-label)),2)
				centroid.append([cX,cY,label])
		cv2.namedWindow('Detection Result', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Detection Result', self.width, self.height)
		cv2.imshow("Detection Result",roi_image)
		return centroid

	def matching_centroid(self,centroid,starting_point,det_r):
		# matching coordinate of roi image to original image
		# write res file
		top_left_x=starting_point[0]
		top_left_y=starting_point[1]
		original_image=cv2.imread(self.image_path)
		text_name=self.output_path+"/res_"+self.image_path+'.txt'
		res_file=open(text_name, 'w+')
		# inside each iteration, write res file and plot circles
		for [x,y,label] in centroid:
			original_x=x+top_left_x
			original_y=y+top_left_y
			cv2.circle(original_image,(original_x,original_y),det_r,(0,255*label,255*(1-label)),2)
			string_to_write="- ["+str(original_x)+","+str(original_y)+","+str(det_r)+","+str(label)+"]"
			res_file.write(string_to_write+'\n')
		# showing result image
		cv2.namedWindow('Detection Result: original image', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Detection Result: original image', self.width, self.height)
		cv2.imshow("Detection Result: original image",original_image)
		name=self.output_path+"/output_"+self.image_path
		cv2.imwrite(name,original_image)
		res_file.close()

	def run(self):
		# run all methods above to obtain and save results
		starting_point,roi_image=self.select_roi()
		binary_img=self.extract_binary_image()
		det_r=self.finding_radius(binary_img)
		centroid=self.circle_len_detection(det_r,binary_img,roi_image)
		self.matching_centroid(centroid,starting_point,det_r)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

