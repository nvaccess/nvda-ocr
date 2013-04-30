# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# add-on Name
	"addon-name" : "ocr",
	# Add-on summary
	# TRANSLATORS: Summary for this add-on to be shown on installation and add-on information.
	"addon-summary" : _("OCR"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on installation and add-on information
	"addon-description" : _("""Performs optical character recognition (OCR) to extract text from an object which is inaccessible.
The Tesseract OCR engine is used.
To perform OCR, move to the object in question using object navigation and press NVDA+r.
You can set the OCR recognition language by going to the NVDA preferences menu and selecting OCR settings."""),
	# version
	"addon-version" : "2013.1",
	# Author(s)
	"addon-author" : "NV Access Limited & other contributors",
	# URL for the add-on documentation support
	"addon-url" : None
}

import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = ["addon/globalPlugins/ocr/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
