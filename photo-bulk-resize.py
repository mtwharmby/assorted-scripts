from PIL import Image
import glob
import os

def chkMkDir(dirName):
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	return


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
	try:
		currentImg = Image.open(os.path.join(workDir, jpg))
		currentImg.load()
	except:
		print "Problems reading file "+str(currentImg)
