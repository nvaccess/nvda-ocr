"""Download and extract dependencies.
"""

import os
import re
import urllib
import fnmatch
import shutil
import zipfile

TESSERACT_DOWNLOAD_URL = "http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02-win32-portable.zip"
PIL_DOWNLOAD_URL = "http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DEPS_DIR = os.path.join(ROOT_DIR, "deps")
PLUGIN_DIR = os.path.join(ROOT_DIR, "addon", "globalPlugins", "ocr")

depFiles = set()

def downloadDeps():
	try:
		os.mkdir(DEPS_DIR)
	except OSError:
		pass

	urls = [TESSERACT_DOWNLOAD_URL, PIL_DOWNLOAD_URL]

	print("Downloading dependencies")
	for url in urls:
		fn = os.path.basename(url)
		localPath = os.path.join(DEPS_DIR, fn)
		depFiles.add(localPath)
		if os.path.isfile(localPath):
			print("%s already downloaded" % fn)
			continue
		print "Downloading %s" % fn
		# Download to a temporary path in case the download aborts.
		tempPath = localPath + ".tmp"
		urllib.urlretrieve(url, tempPath)
		os.rename(tempPath, localPath)

TESSERACT_FILES = ["tesseract.exe", "tessdata/*",
	"doc/AUTHORS", "doc/COPYING"]
def extractTesseract():
	for zfn in depFiles:
		if fnmatch.fnmatch(zfn, "*/tesseract-ocr-*-win32-portable.zip"):
			break
	else:
		assert False

	tessDir = os.path.join(PLUGIN_DIR, "tesseract")
	print "Extracting Tesseract"
	shutil.rmtree(tessDir, ignore_errors=True)
	with zipfile.ZipFile(zfn) as zf:
		for realFn in zf.namelist():
			if realFn.endswith("/"):
				continue
			# Strip the top level distribution directory.
			fn = realFn.split("/", 1)[1]
			extractFn = os.path.join(tessDir, fn.replace("/", os.path.sep))
			if not any(fnmatch.fnmatch(fn, pattern) for pattern in TESSERACT_FILES):
				continue
			try:
				os.makedirs(os.path.dirname(extractFn))
			except OSError:
				pass
			with zf.open(realFn) as inf, file(extractFn, "wb") as outf:
				shutil.copyfileobj(inf, outf)

def extractPil():
	pilDir = os.path.join(PLUGIN_DIR, "PIL")
	print "Extracting PIL"
	shutil.rmtree(pilDir, ignore_errors=True)
	try:
		os.mkdir(pilDir)
	except OSError:
		pass

	with zipfile.ZipFile(os.path.join(DEPS_DIR, os.path.basename(PIL_DOWNLOAD_URL))) as zf:
		for realFn in zf.namelist():
			if not realFn.startswith("PLATLIB/PIL/") or realFn.endswith("/"):
				continue
			fn = os.path.basename(realFn)
			extractFn = os.path.join(pilDir, fn)
			with zf.open(realFn) as inf, file(extractFn, "wb") as outf:
				shutil.copyfileobj(inf, outf)

def main():
	downloadDeps()
	extractTesseract()
	extractPil()

if __name__ == "__main__":
	main()
