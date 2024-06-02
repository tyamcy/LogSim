# -*- coding: utf-8 -*-
"""
This will generate the .pot and .mo files for the application domain and
languages defined below.

The .po and .mo files are placed as per convention in

"appfolder/locale/lang/LC_MESSAGES"

The .pot file is placed in the locale folder.

This script or something similar should be added to your build process.

The actual translation work is normally done using a tool like poEdit or
similar, it allows you to generate a particular language catalog from the .pot
file or to use the .pot to merge new translations into an existing language
catalog.
"""

import app_const as appC
import os
import sys
import subprocess

# Remove English as source code strings are in English
supportedLang = [l for l in appC.supLang if l != u"en"]

appFolder = os.getcwd()

# Setup paths to Python I18N tools/utilities
pyExe = sys.executable
pyFolder = os.path.split(pyExe)[0]
pyToolsFolder = os.path.join(pyFolder, 'Tools', 'i18n')
pyGettext = os.path.join(pyToolsFolder, 'pygettext.py')
pyMsgfmt = os.path.join(pyToolsFolder, 'msgfmt.py')
outFolder = os.path.join(appFolder, 'locale')

# Generate .pot file command
gtOptions = f'-a -d "{appC.langDomain}" -o "{os.path.join(outFolder, appC.langDomain)}.pot" -p "{outFolder}" "{appFolder}"'
tCmd = f'"{pyExe}" "{pyGettext}" {gtOptions}'
print("Generating the .pot file")
print("cmd:", tCmd)
rCode = subprocess.call(tCmd, shell=True)
print("return code:", rCode, "\n\n")

# Generate .mo files for supported languages
for tLang in supportedLang:
    langDir = os.path.join(appFolder, f'locale\\{tLang}\\LC_MESSAGES')
    poFile = os.path.join(langDir, f'gui.po')
    tCmd = f'"{pyExe}" "{pyMsgfmt}" "{poFile}"'
    
    print("Generating the .mo file for", tLang)
    print("cmd:", tCmd)
    rCode = subprocess.call(tCmd, shell=True)
    print("return code:", rCode, "\n\n")

