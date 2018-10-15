#!/usr/bin/python
####################################################################################################
#
# Download & Install DMG
#
####################################################################################################
#
# DESCRIPTION:
#
# This will Download a DMG file from a user defined site then Install DMG.
# The way it should work means if the download URL is versioned the script will find the still get the correct link, even if the download URL changes.
# Currently setup to only work with single .app files in the DMG.
#
# Many thanks to Caine Horr, I copied their 'Download and Install Chrome' script from:
#  https://www.jamf.com/jamf-nation/discussions/20894/install-latest-version-of-google-chrome-without-re-packaging
# and I marked the code I used with #* in the comments and used the script as a template.
#
# HOW TO USE:
#
# Find the download page that contains the DMG (https://dl.url.com/)
# Either fill the Static code or in a Jamf policy change the $4, $5, $6 and $7 fields as the are indicated
#
####################################################################################################
#
# HISTORY:
#
# Created by Andrew Hopcroft on 2018-10-15
#
# v1.0 - 2018-10-15 - Andrew Hopcroft
# Download & Install DMG
#
####################################################################################################

# Import libraries for basic command line functions
import os, sys, time, re, urllib2, subprocess, glob

# VARIABLES

# Change after the else to set them static
weburl = sys.argv[4] if sys.argv[4] != '' else 'https://www.videolan.org/vlc/download-macosx.html'
#File host page [eg: https://www.videolan.org/vlc/download-macosx.html]
itemname = sys.argv[5] if sys.argv[5] != '' else ''
#File or folder to move to Apps folder [not in use yet]
live = True if sys.argv[6].lower() == 'true' else False
#Finished testing, run live [True/*False*]
verbose = False if sys.argv[7].lower() == 'false' else True
#Verbose logging [*True*/False]

print "URL: " + weburl
print "Item: " + itemname
print "Output: [" + ("Testing" if not live else "Live, will install") + "] | [" + ("Verbose logging" if verbose else "No verbose logging") + "]"

somethingfailed = False

# Get website content
response = urllib2.urlopen(weburl)
webdata = response.read()
if verbose: print webdata

urllist = re.findall('(".*?")', webdata) # Pull out everything that is in quotes ""
somethingfailed = True
for i in urllist : # Find the first .dmg link
	if ".dmg" in i :
		dirtyurl = i
		somethingfailed = False
		break

if somethingfailed : #Errors?
	print "No DMG found in page, please check the page content. Ending the script."
	exit()

# Try to fix the URL if there are problems.
dirtyurl = dirtyurl.replace('"',"") # Remove the quotes from the url
goodurlstart = ["htt","sft","ftp"] # you can add to this list
if dirtyurl[:3] not in goodurlstart :
	somethingfailed = True
	if ("//" == dirtyurl[:2]):
		dirtyurl = "https:" + dirtyurl
		somethingfailed = False
	elif ("://" == dirtyurl[:3]):
		dirtyurl = "https" + dirtyurl
		somethingfailed = False
	else:
		if verbose: print "error " + dirtyurl[:2]

if somethingfailed : #Errors?
	print "Something is wrong with the Download URL."
	exit()


url = dirtyurl.replace(" ","%20") # URLs dont like spaces
lastslash = dirtyurl.rfind("/")
dmg = dirtyurl.replace(dirtyurl[:lastslash+1],"") # Using the position of the last slash we can find the name of the DMG

if verbose: print "Dirty:"+ dirtyurl
if verbose: print "URL: "+url
if verbose: print "DMG: "+dmg

# *Download vendor supplied DMG file into /tmp/
os.system('curl -L '+url+' -o "/tmp/'+dmg+'"')
if verbose: print os.listdir('/tmp/')
if verbose: print "Downloaded to /tmp/"+dmg

# *Mount vendor supplied DMG File
if os.path.isfile('/tmp/' + dmg ):
	os.system('hdiutil attach "/tmp/' + dmg + '" -nobrowse')
	if verbose: print "Mounted the DMG: " + '/tmp/' + dmg
	if verbose: print os.listdir('/Volumes/')
else:
	if verbose: print "Error finding file at: " + '/tmp/' + dmg
	exit()

# Get the correct volumes path
somethingfailed = True
volumeslist = os.listdir('/Volumes/')
dmgwords = dmg.replace('-', ' ').replace('_', ' ').lower().split(' ')
for vol in volumeslist:
	v = vol.replace('-', ' ').replace('_', ' ').lower().split(' ')
	for a in dmgwords:
		for b in v:
			if verbose: print "Checking " + a + " in " + b
			if (a == b):
				somethingfailed = False
				mount = vol
				break
			else: continue
		else: continue
		break
	else: continue
	break

if somethingfailed : #Errors?
	print "Mount point not found. Ending the script."
	exit()

if verbose: print "MOUNT: " + mount

# This needs to be fixed so it will handle errors better.
# ToDo: Make it so that $7 will work for expected *anythings*
somethingfailed = True
applist =  os.listdir('/Volumes/'+mount)
if itemname == '' :
	for apps in applist:
		if verbose: print apps
		if (apps[-4:] == ".app"):
			somethingfailed = False
			app = apps
			break
		else:continue
		break
else:
	#todo!
	print "We've got items but no way to manage that yet!"

if somethingfailed : #Errors?
	print "Couldn't find the .app file. Ending the script."
	exit()

if verbose: print "APP: " + app

# *Copy contents of vendor supplied DMG file to /Applications/
# *Preserve all file attributes and ACLs
if live:
	os.system("cp -pPR '/Volumes/" + mount + "/" + app + "' /Applications/")
	if verbose: print "Copy of .app completed"
else:
	if verbose: print "__no copying till tested__"

# *Identify the correct mount point for the vendor supplied DMG file
somethingfailed = True
hdiout = os.popen("(hdiutil info)").readlines()
for line in hdiout:
	if mount in line:
		if verbose: print line
		mounted = line[:(line.find("\t"))]
		somethingfailed = False
		break
	else:continue
	break

if somethingfailed : #Errors?
	print "Failed to locate the mount location. Ending the script."
	exit()

if verbose: print "Mounted: " + mounted

# *Unmount the vendor supplied DMG file
somethingfailed = True
os.system("hdiutil detach " + mounted)
hdiout = os.popen("(hdiutil info)").readlines()
if mounted not in hdiout:
	somethingfailed = False
	if verbose: print "Unmount worked."

if somethingfailed : #Errors?
	print "Failed to unmount the volume. Ending the script."
	exit()

# *Remove the downloaded vendor supplied DMG file
os.system("rm -f '/tmp/" + dmg + "'")
if verbose: print "Removed the installer from the tmp folder"
