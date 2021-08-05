# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 12:41:43 2021

@author: aydan

Code to run displayregion.py as the ml folder is meant to be a package
"""


from ml.displayregion import main
import sys
# str(sys.argv[1]) = 'D:/githubfiles/ASTR490/ml/config.ini'
# str(sys.argv[2]) = e.g. noregion, baseparams, etc. 

main(str(sys.argv[2]),str(sys.argv[1]))

# print ('First argument:',  str(sys.argv[0]))
# print ('Second argument:',  str(sys.argv[1]))
# print ('Third argument:',  str(sys.argv[2]))

# =============================================================================
# Code to run runner.py
# python runner.py 'D:/githubfiles/ASTR490/ml/config.ini' noregion
# =============================================================================
