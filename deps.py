"""Download and extract dependencies.
"""

import os
import re
import urllib
import fnmatch
import shutil
import zipfile
import tarfile

# Sometimes, different packages have different versions.
TESSERACT_VERSIONS = ("3.02.02", "3.02")
TESSERACT_DOWNLOAD_URL = "http://code.google.com/p/tesseract-ocr/downloads/list"
PIL_DOWNLOAD_URL = "http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DEPS_DIR = os.path.join(ROOT_DIR, "deps")
PLUGIN_DIR = os.path.join(ROOT_DIR, "addon", "globalPlugins", "ocr")

depFiles = set()

def getTesseractUrls():
	data = urllib.urlopen(TESSERACT_DOWNLOAD_URL).read()
	versionRe = "(?:%s)" % "|".join(re.escape(ver) for ver in TESSERACT_VERSIONS)
	for m in re.finditer(
		r'href="(.*?tesseract-ocr-%s(?:'
			r'-win32-portable\.zip|'
			# Language data
			r'\.[a-z]{3}(?:_[a-z]{3})?\.tar\.gz'
			r'))"' % versionRe,
		data
	):
		# Google Code doesn't seem to include the http: protocol prefix.
		yield "http:" + m.group(1)

def downloadDeps():
	try:
		os.mkdir(DEPS_DIR)
	except OSError:
		pass

	urls = list(getTesseractUrls())
	urls.append(PIL_DOWNLOAD_URL)

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

def extractTesseractLangs():
	print "Extracting Tesseract languages"
	dataDir = os.path.join(PLUGIN_DIR, "tesseract", "tessdata")
	for tfn in depFiles:
		if not fnmatch.fnmatch(tfn, "*/tesseract-ocr-*.*.tar.gz"):
			continue
		with tarfile.open(tfn) as tf:
			for info in tf:
				if info.isdir():
					continue
				fn = os.path.basename(info.name)
				extractFn = os.path.join(dataDir, fn)
				inf = tf.extractfile(info)
				outf = file(extractFn, "wb")
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
	extractTesseractLangs()
	extractPil()

if __name__ == "__main__":
	main()
