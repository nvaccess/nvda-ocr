"""Output the URLs for the Tesseract Win32 portable package and all language data archives.
"""

import re
import urllib2

# Sometimes, different packages have different versions.
VERSIONS = ("3.02.02", "3.02")
DOWNLOAD_URL = "http://code.google.com/p/tesseract-ocr/downloads/list"

def getUrls():
	data = urllib2.urlopen(DOWNLOAD_URL).read()
	versionRe = "(?:%s)" % "|".join(re.escape(ver) for ver in VERSIONS)
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

def main():
	for url in getUrls():
		print(url)

if __name__ == "__main__":
	main()
