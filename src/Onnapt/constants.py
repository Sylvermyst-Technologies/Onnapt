'''
Created on 21 Oct 2014

    Copyright (c) 2014 Brendan Gray and Sylvermyst Technologies

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    
'''


from PyQt4.QtCore import Qt


debugModeEnabled = True
targetFPS = 60

settingsFileName = 'laststate.cfg'

acceptedInputMethods = ['Space', 'Ctrl']

magicWidthSizeFactor = 8 # The maximum width to height ratio of the time display
magicHeightSizeFactor = 0.9 # The maximum fraction of the available height that may be used by the timer display 

scrambleDisplayHeightLimits = [10, 320]

timerDisplayMinimumHeight = 24
timerDisplayDefaultFontSize = 16 # Point
bottomDisplayMinimumHeight = 200

scrambleBufferSize = 12 # Number of scrambles to prepare in advance
scrambleUpdateInterval = 500 # Time in milliseconds to try and add a new scramble to the scramble buffer
scrambleForceUpdateAttempts = 10 # Force a new update attempt after # failed attempts.

inspection1stWarnFrac = 1 - 8.0/15.0
inspection2ndWarnFrac = 1 - 12.0/15.0
inspectionRunover = 2 





