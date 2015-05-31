from PIL import Image
import glob
import numpy as np
import os

def chkMkDir(dirName):
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	return

def imgSizeFinder(img, newSize=1280):
	imgDims = img.size
	dimMax = max(imgDims)

	if (dimMax <= newSize):
		width = imgDims[0]
		height = imgDims[1]
	else:
		width = int(np.around((float)imgDims[0]/float(dimMax)*newSize))
		height = int(np.around((float)imgDims[1]/float(dimMax)*newSize))

	return (width, height)


#Do we have a list of files
#Are we creating thumbs too

#Create output directory to store resized images + thumbs
workDir = os.getcwd()
outDir = os.path.join(workDir, "resized")
chkMkDir(outDir)

if makeThumbs:
	thumbDir = os.path.join(outDir, "thumbs")
	chkMkDir(thumbDir)

#For each file in w/d: import image; resize and save; make thumbnail & save
inputFiles = glob.glob("*.jpg")

for jpg in inputFiles:
	currentImg = None
	try:
		currentImg = Image.open(os.path.join(workDir, jpg))
	except:
		print "Problems reading file "+str(currentImg)

	outImgSize = imgSizeFinder(currentImg)