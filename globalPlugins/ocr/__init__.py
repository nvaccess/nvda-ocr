"""NVDA OCR plugin
This plugin uses Tesseract for OCR: http://code.google.com/p/tesseract-ocr/
It also uses the Python Imaging Library (PIL): http://www.pythonware.com/products/pil/
@author: James Teh <jamie@nvaccess.org>
@copyright: 2011 NV Access Limited
@license: GNU General Public License version 2.0
@version: 2011-11-09-01
"""

import sys
import os
import tempfile
import subprocess
from xml.parsers import expat
from collections import namedtuple
import globalPluginHandler
import api
import textInfos.offsets
import ui

PLUGIN_DIR = os.path.dirname(__file__)
TESSERACT_EXE = os.path.join(PLUGIN_DIR, "tesseract", "tesseract.exe")

# Add bundled copy of PIL to module search path.
sys.path.append(os.path.join(PLUGIN_DIR, "PIL"))
import ImageGrab
del sys.path[-1]

IMAGE_RESIZE_FACTOR = 2

OcrWord = namedtuple("OcrWord", ("offset", "left", "top"))

class HocrParser(object):

	def __init__(self, xml, leftCoordOffset, topCoordOffset):
		self._leftCoordOffset = leftCoordOffset
		self._topCoordOffset = topCoordOffset
		parser = expat.ParserCreate("utf-8")
		parser.StartElementHandler = self._startElement
		parser.EndElementHandler = self._endElement
		parser.CharacterDataHandler = self._charData
		self._textList = []
		self.textLen = 0
		self.lines = []
		self.words = []
		self._hasBlockHadContent = False
		parser.Parse(xml)
		self.text = "".join(self._textList)
		del self._textList

	def _startElement(self, tag, attrs):
		if tag in ("p", "div"):
			self._hasBlockHadContent = False
		elif tag == "span":
			cls = attrs["class"]
			if cls == "ocr_line":
				self.lines.append(self.textLen)
			elif cls == "ocr_word":
				# Get the coordinates from the bbox info specified in the title attribute.
				title = attrs.get("title")
				prefix, l, t, r, b = title.split(" ")
				self.words.append(OcrWord(self.textLen,
					self._leftCoordOffset + int(l) / IMAGE_RESIZE_FACTOR,
					self._topCoordOffset + int(t) / IMAGE_RESIZE_FACTOR))

	def _endElement(self, tag):
		pass

	def _charData(self, data):
		if data.isspace():
			if not self._hasBlockHadContent:
				# Strip whitespace at the start of a block.
				return
			# All other whitespace should be collapsed to a single space.
			data = " "
			if self._textList and self._textList[-1] == data:
				return
		self._hasBlockHadContent = True
		self._textList.append(data)
		self.textLen += len(data)

class OcrTextInfo(textInfos.offsets.OffsetsTextInfo):

	def __init__(self, obj, position, parser):
		self._parser = parser
		super(OcrTextInfo, self).__init__(obj, position)

	def copy(self):
		return self.__class__(self.obj, self.bookmark, self._parser)

	def _getTextRange(self, start, end):
		return self._parser.text[start:end]

	def _getStoryLength(self):
		return self._parser.textLen

	def _getLineOffsets(self, offset):
		start = 0
		for end in self._parser.lines:
			if end > offset:
				return (start, end)
			start = end
		return (start, self._parser.textLen)

	def _getWordOffsets(self, offset):
		start = 0
		for word in self._parser.words:
			if word.offset > offset:
				return (start, word.offset)
			start = word.offset
		return (start, self._parser.textLen)

	def _getPointFromOffset(self, offset):
		for nextWord in self._parser.words:
			if nextWord.offset > offset:
				break
			word = nextWord
		else:
			# No matching word, so use the top left of the object.
			l, t, w, h = self.obj.location
			return textInfos.Point(l, t)
		return textInfos.Point(word.left, word.top)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def script_ocrNavigatorObject(self, gesture):
		nav = api.getNavigatorObject()
		left, top, width, height = nav.location
		img = ImageGrab.grab(bbox=(left, top, left + width, top + height))
		# Tesseract copes better if we convert to black and white...
		img = img.convert(mode='L')
		# and increase the size.
		img = img.resize((width * IMAGE_RESIZE_FACTOR, height * IMAGE_RESIZE_FACTOR))
		baseFile = os.path.join(tempfile.gettempdir(), "nvda_ocr")
		try:
			imgFile = baseFile + ".bmp"
			img.save(imgFile)

			ui.message("Performing OCR")
			# Hide the Tesseract window.
			si = subprocess.STARTUPINFO()
			si.dwFlags = subprocess.STARTF_USESHOWWINDOW
			si.wShowWindow = subprocess.SW_HIDE
			subprocess.check_call((TESSERACT_EXE, imgFile, baseFile, "hocr"),
				startupinfo=si)
		finally:
			try:
				os.remove(imgFile)
			except OSError:
				pass
		try:
			hocrFile = baseFile + ".html"

			parser = HocrParser(file(hocrFile).read(),
				left, top)
		finally:
			try:
				os.remove(hocrFile)
			except OSError:
				pass

		# Let the user review the OCR output.
		nav.makeTextInfo = lambda position: OcrTextInfo(nav, position, parser)
		api.setReviewPosition(nav.makeTextInfo(textInfos.POSITION_FIRST))
		ui.message("Done")

	__gestures = {
		"kb:NVDA+r": "ocrNavigatorObject",
	}
