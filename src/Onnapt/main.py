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

import threading

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QTimer, QByteArray

from Onnapt.constants import *
from Onnapt.timer import PuzzleTimer
from Onnapt.scramblebuffer import ScrambleBuffer
from Onnapt.cubepicture import CubePicture
from Onnapt.utilities import timeToStr, makeAllWhitespaceSpaces

from Onnapt.scrambler import CubeScramblerByRandomTurns


class MainScreen(QtGui.QMainWindow):

    def __init__(self):

        super(MainScreen, self).__init__()  # Call the constructor of this class's parent
        self.prepare()
        self.loadSettings()

        self.initUI()
        
        self.fpsTimer = QTimer()
        self.fpsTimer.timeout.connect(self.updateDisplay)
        self.fpsTimer.start(1000 / targetFPS)  # set targetFPS in constants.

        self.newSolve()




    def prepare(self):
        '''
        Initialises variables that need to be set before the GUI is initialised.
        '''

        self.ctrlkeytracker = [0, 0]  # Keeps track of how many Ctrl keys are pressed now [0], and how many were pressed before the last change [1].
        self.puzzleTimer = PuzzleTimer()
        self.inspectionTimer = PuzzleTimer()
        self.justStopped = False
        self.justStartedInspection = False
        self.timerReady = True

        self.inspectionTimeLimit = 15
        self.inspectionEnabled = 1

        self.decimalPlaces = 2
        self.inputMethod = 'Space'
        
        self.cubeImageWidth = bottomDisplayMinimumHeight
        self.bottomPanelHeight = bottomDisplayMinimumHeight
        
        self.timerDisplaySplitterSizes = None
        self.bottomPanelSplitterSizes = None

        self.newScrambleFont = None
        
        self.lastWindowLeft = 300
        self.lastWindowTop = 300
        self.lastWindowWidth = 700
        self.lastWindowHeight = 500

        self.scrambleDisplayHeight = 16

        self.cubeColours = 'wgrboy'
        
        self.changePuzzleType(puzzle='NNNcube', size=3)



    def initUI(self):
        '''
        Initialises the UI layout and widgets.
        '''


        # timerWindow = QtGui.QWidget()
        self.scramblesplitter = QtGui.QSplitter(Qt.Vertical)
        self.bottomSplitter = QtGui.QSplitter(Qt.Horizontal)

        self.scrambleDisplay = ScrambleDisplay(self.scramblesplitter, "Scramble goes here")
        self.scrambleDisplay.setMinimumHeight(scrambleDisplayHeightLimits[0])
        self.scrambleDisplay.setMaximumHeight(scrambleDisplayHeightLimits[1])
        self.scrambleDisplay.setWordWrap(True)
        if not self.newScrambleFont is None:
            self.scrambleDisplay.setFont(self.newScrambleFont)
        else:
            displayFont = self.scrambleDisplay.font()
            displayFont.setPointSize(timerDisplayDefaultFontSize)
            self.scrambleDisplay.setFont(displayFont)
             
        
        self.scramblesplitter.addWidget(self.scrambleDisplay)
        
        self.timerDisplay = TimerDisplay("")
        self.timerDisplay.setMinimumHeight(timerDisplayMinimumHeight)
        self.scramblesplitter.addWidget(self.timerDisplay)
        self.scramblesplitter.setCollapsible(1, False)
        
        placeHolder = QtGui.QLabel("Placeholder")
        self.bottomSplitter.addWidget(placeHolder)
        
        self.cubePicture = CubePicture(self, self.puzzleSize, self.cubeColours)
        self.cubePicture.setMinimumHeight(bottomDisplayMinimumHeight)
        self.bottomSplitter.addWidget(self.cubePicture)

        self.scramblesplitter.addWidget(self.bottomSplitter)
        
        self.setCentralWidget(self.scramblesplitter)

        self.buildMenu()

        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exitAction)

        self.setGeometry(self.lastWindowLeft, self.lastWindowTop, self.lastWindowWidth, self.lastWindowHeight)
        #self.scrambleDisplay.setMaximumWidth(self.width())
        self.scramblesplitter.setSizes([self.scrambleDisplayHeight, self.scramblesplitter.height()-self.scrambleDisplayHeight-bottomDisplayMinimumHeight, self.bottomPanelHeight])
        self.bottomSplitter.setSizes([self.bottomSplitter.width()-self.cubeImageWidth, self.cubeImageWidth])

        if not self.timerDisplaySplitterSizes is None:
            self.scramblesplitter.restoreState(self.timerDisplaySplitterSizes) 
        if not self.bottomPanelSplitterSizes is None:
            self.bottomSplitter.restoreState(self.bottomPanelSplitterSizes) 

        
        #self.scrambleDisplay.setFrameStyle(QtGui.QFrame.StyledPanel)
        self.timerDisplay.setFrameStyle(QtGui.QFrame.StyledPanel)
        #self.cubePicture.setFrameStyle(QtGui.QFrame.StyledPanel)

        
        self.setWindowTitle('Oh No! Not Another Puzzle Timer')
        self.show()



    def buildMenu(self):
        '''
        Populates the menu bar
        '''

        menubar = self.menuBar()

        # ===  File menu  ===

        fileMenu = menubar.addMenu('&File')

        exitAction = QtGui.QAction('E&xit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # ===  Options menu ===

        optionsMenu = menubar.addMenu('&Options')

        self.optInputSubMenu = optionsMenu.addMenu('&Input')

        self.optInputMethods = QtGui.QActionGroup(self, exclusive=True)
        self.optInputSpace = QtGui.QAction("&Spacebar", self.optInputMethods, checkable=True)
        self.optInputSubMenu.addAction(self.optInputSpace)
        self.optInputCtrl = QtGui.QAction("&Ctrl keys", self.optInputMethods, checkable=True)
        self.optInputSubMenu.addAction(self.optInputCtrl)
        if self.inputMethod == 'Space':
            self.optInputSpace.setChecked(True)
        elif self.inputMethod == 'Ctrl':
            self.optInputCtrl.setChecked(True)
        self.optInputMethods.triggered.connect(self.changeInputMethod)

        self.optInspectionSubMenu = optionsMenu.addMenu('Inspection &Timer')

        self.optInspectionEnabled = QtGui.QAction("&Enabled", self, checkable=True)
        self.optInspectionEnabled.triggered.connect(self.toggleInspectionTimer)
        self.optInspectionSubMenu.addAction(self.optInspectionEnabled)
        if self.inspectionEnabled:
            self.optInspectionEnabled.setChecked(True)
        self.optInspectionChange = QtGui.QAction("&Change time... (" + str(self.inspectionTimeLimit) + " s)", self)
        self.optInspectionChange.triggered.connect(self.changeInspectionTime)
        self.optInspectionSubMenu.addAction(self.optInspectionChange)

        self.optDecimalsChangeAction = QtGui.QAction("&Decimal places: " + str(self.decimalPlaces), self)
        self.optDecimalsChangeAction.triggered.connect(self.changeDecimalPlaces)
        optionsMenu.addAction(self.optDecimalsChangeAction)

        self.scrambleFontAction = QtGui.QAction("&Scramble Font...", self)
        self.scrambleFontAction.triggered.connect(self.changeScrambleFont)
        optionsMenu.addAction(self.scrambleFontAction)






    def loadSettings(self):
        '''
        If a settings file exists, then the settings are loaded from it. These override the default values.
        '''

        try:
            with open(settingsFileName) as settingsFile:
                settings = settingsFile.readlines()
        except IOError:
            print("Couldn't read last state from file. Ignoring...")
            return

        for i in range(len(settings)):
            try:
                line = makeAllWhitespaceSpaces(settings[i]).split(' ')

                if line[0] == 'SIZE':
                    self.lastWindowWidth = int(line[1])
                    self.lastWindowHeight = int(line[2])

                elif line[0] == 'POSITION':
                    self.lastWindowLeft = int(line[1])
                    self.lastWindowTop = int(line[2])

                elif line[0] == 'TIME_DECMALStretchyCenteredDisplay_PLACES':
                    self.decimalPlaces = int(line[1])

                elif line[0] == 'INPUT_METHOD' and line[1] in acceptedInputMethods:
                    self.inputMethod = line[1]

                elif line[0] == 'INSPECTION_ENABLED' and line[1] in ['0', '1']:
                    self.inspectionEnabled = int(line[1])

                elif line[0] == 'INSPECTION_TIME':
                    self.inspectionTimeLimit = int(line[1])

                elif line[0] == 'SCRAMBLE_FONT':
                    fontStartPos = settings[i].find(line[1])
                    self.newScrambleFont = QtGui.QFont()
                    self.newScrambleFont.fromString(settings[i][fontStartPos:].strip())

                elif line[0] == 'TIMER_DISPLAY_SETTINGS':
                    self.timerDisplaySplitterSizes = QByteArray.fromHex(line[1].split("'")[1])

                elif line[0] == 'BOTTOM_PANEL_SETTINGS':
                    self.bottomPanelSplitterSizes = QByteArray.fromHex(line[1].split("'")[1])
                    
            except:
                print("Error reading line", i, "in settings file")
                print("    " + settings[i].strip())
            

    def saveSettings(self):
        '''
        If a settings file exists, then the settings are loaded from it. These override the default values.
        '''

        with open(settingsFileName, 'w') as settingsFile:
            settingsFile.write('POSITION ' + str(self.geometry().left()) + ' ' + str(self.geometry().top()) + '\n')
            settingsFile.write('SIZE ' + str(self.width()) + ' ' + str(self.height()) + '\n')
            settingsFile.write('TIME_DECMAL_PLACES ' + str(self.decimalPlaces) + '\n')
            settingsFile.write('INPUT_METHOD ' + self.inputMethod + '\n')
            settingsFile.write('INSPECTION_ENABLED ' + str(self.inspectionEnabled) + '\n')
            settingsFile.write('INSPECTION_TIME ' + str(self.inspectionTimeLimit) + '\n')
            settingsFile.write('SCRAMBLE_FONT ' + str(self.scrambleDisplay.font().toString()) + '\n')
            settingsFile.write('TIMER_DISPLAY_SETTINGS ' + str(self.scramblesplitter.saveState().toHex()) + '\n')
            settingsFile.write('BOTTOM_PANEL_SETTINGS ' + str(self.bottomSplitter.saveState().toHex()) + '\n')




    def updateDisplay(self):
        '''
        Updates the display
        '''

        if self.inspectionTimer.isRunning():
            currentTime = self.inspectionTimeLimit - self.inspectionTimer.getTime()
            self.timerDisplay.setText(timeToStr(currentTime, self.decimalPlaces))

            if currentTime < 0:
                palette = self.timerDisplay.palette()
                palette.setColor(QtGui.QPalette.WindowText, Qt.red)
                self.timerDisplay.setPalette(palette)
            elif currentTime < self.inspectionTimeLimit * inspection2ndWarnFrac:
                palette = self.timerDisplay.palette()
                palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255,128,0))
                self.timerDisplay.setPalette(palette)
            elif currentTime < self.inspectionTimeLimit * inspection1stWarnFrac:
                palette = self.timerDisplay.palette()
                palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(192,192,32))
                self.timerDisplay.setPalette(palette)
            else:
                palette = self.timerDisplay.palette()
                palette.setColor(QtGui.QPalette.WindowText, Qt.darkGreen)
                self.timerDisplay.setPalette(palette)

        else:
            colour = self.palette().color(QtGui.QPalette.WindowText)
            palette = self.timerDisplay.palette()
            palette.setColor(QtGui.QPalette.WindowText, colour)
            self.timerDisplay.setPalette(palette)

            currentTime = self.puzzleTimer.getTime()
            self.timerDisplay.setText(timeToStr(currentTime, self.decimalPlaces))


            



    def keyPressEvent(self, event):
        '''
        Handles key presses anywhere in the program.
        '''

        if self.inputMethod == 'Ctrl' and event.key() in [Qt.Key_Control, Qt.Key_Meta]:  # Either a Ctrl key in Windows and Linux, or the Command key of a Mac
            if int(event.nativeScanCode()) < 80:
                # This is a messy work around, and may not always work.
                # scan code gave 25 and 285 on my Windows 7 machine, and 37 and 105 on my Ubuntu machine for L and R Ctrl respectively.
                # It would be better if Qt could tell L and R Ctrl apart, but it seems that it can't.
                # print("Left Ctrl pressed")
                self.ctrlkeytracker[1] = self.ctrlkeytracker[0]
                self.ctrlkeytracker[0] += 1
            else:
                # print("Right Ctrl pressed")
                self.ctrlkeytracker[1] = self.ctrlkeytracker[0]
                self.ctrlkeytracker[0] += 1
            self.handleCtrlSituation()

        if self.inputMethod == 'Space' and event.key() == Qt.Key_Space and not event.isAutoRepeat():

            self.justStartedInspection = False
            if self.puzzleTimer.isRunning():
                self.puzzleTimer.stop()
                self.justStopped = True
                self.newSolve()
            else:
                displayFont = self.timerDisplay.font()
                displayFont.setItalic(True)
                self.timerDisplay.setFont(displayFont)

        if debugModeEnabled:
            if event.key() == Qt.Key_A:
                self.puzzleTimer.startTime -= 60
            if event.key() == Qt.Key_S:
                self.puzzleTimer.startTime -= 600
            if event.key() == Qt.Key_D:
                self.puzzleTimer.startTime -= 3600


    def keyReleaseEvent(self, event):
        '''
        Handles key presses anywhere in the program.
        '''

        if self.inputMethod == 'Ctrl' and event.key() in [Qt.Key_Control, Qt.Key_Meta]:  # Either a Ctrl key in Windows and Linux, or the Command key of a Mac
            if int(event.nativeScanCode()) < 80:
                # This is a messy work around, and I'm not sure it will always work.
                # print("Left Ctrl released")
                self.ctrlkeytracker[1] = self.ctrlkeytracker[0]
                self.ctrlkeytracker[0] -= 1
            else:
                # print("Right Ctrl released")
                self.ctrlkeytracker[1] = self.ctrlkeytracker[0]
                self.ctrlkeytracker[0] -= 1
            self.handleCtrlSituation()

        if self.inputMethod == 'Space' and event.key() == Qt.Key_Space and not event.isAutoRepeat():
            displayFont = self.timerDisplay.font()
            displayFont.setItalic(False)
            self.timerDisplay.setFont(displayFont)
            
            if self.justStopped:
                self.justStopped = False
                # Prevents the timer from restarting once a Ctrl key is released after stopping.
                
            elif self.inspectionEnabled and not self.inspectionTimer.isRunning():
                self.inspectionTimer.start()
                self.justStartedInspection = True

            elif not self.puzzleTimer.isRunning() and not self.justStartedInspection:
                self.inspectionTimer.stop()
                self.puzzleTimer.start()
                




    def handleCtrlSituation(self):
        '''
        Deals with starting and stopping the timer depending on the current Ctrl situation.
        Should only be called in keyPressEvent or keyReleaseEvent if the Ctrl key was involved in the event. 
        '''
        if self.ctrlkeytracker[0] == 0 and not self.inspectionTimer.isRunning() and not self.puzzleTimer.isRunning():
            self.timerReady = True

        if self.justStopped:
            self.justStopped = False
            # Prevents the timer from restarting once a Ctrl key is released after stopping.
            return

        if self.puzzleTimer.isRunning():
            if self.ctrlkeytracker[0] == 2:
                # If the timer was running, and both Ctrl keys are pressed.
                self.puzzleTimer.stop()
                self.justStopped = True
                self.newSolve()
        else:
            if self.ctrlkeytracker == [1, 2]:
                # If the timer was not running, and one Ctrl key is released after both having been pressed.
                if self.inspectionTimer.isRunning() or self.timerReady:
                    self.inspectionTimer.stop()
                    self.puzzleTimer.start()

            elif self.inspectionEnabled and self.timerReady and self.ctrlkeytracker == [1, 0]:
                self.inspectionTimer.start()
                self.timerReady = False



    def changeDecimalPlaces(self):
        '''
        Toggles the number of decimal places used by the display
        '''

        if self.decimalPlaces == 2:
            self.decimalPlaces = 3
        else:
            self.decimalPlaces = 2

        self.optDecimalsChangeAction.setText("&Decimal places: " + str(self.decimalPlaces))



    def changeInputMethod(self):
        '''
        Responds to a change in the input method
        '''
        if self.optInputSpace.isChecked():
            self.inputMethod = 'Space'
        elif self.optInputCtrl.isChecked():
            self.inputMethod = 'Ctrl'


    def toggleInspectionTimer(self):
        '''
        Toggles whether or not the inspection timer is enabled
        '''
        if self.inspectionEnabled:
            self.inspectionEnabled = 0
        else:
            self.inspectionEnabled = 1


    def changeInspectionTime(self):
        '''
        Bring up a dialog for changing the inspection time
        '''
        newTime, ok = QtGui.QInputDialog.getInteger(self, "Change inspection time", "Enter the new inspection time in seconds", value=self.inspectionTimeLimit)
        if ok:
            self.inspectionTimeLimit = newTime
            self.optInspectionChange.setText("&Change time... (" + str(self.inspectionTimeLimit) + " s)")


    def changeScrambleFont(self):
        '''
        Bring up a dialog for changing the inspection time
        '''
        
        tempFont = QtGui.QFont(self.scrambleDisplay.font())
        tempFont.setFamily(QtGui.QFontInfo(tempFont).family())
        tempFont.setStyle(QtGui.QFont.StyleNormal)
        
        newFont, ok = QtGui.QFontDialog.getFont(tempFont, self, 'Choose the font for the scramble display')
        if ok:
            self.scrambleDisplay.setFont(newFont)
            self.scrambleDisplay.resizeEvent()


    def changePuzzleType(self, puzzle, size=None):
        '''
        
        '''
        if puzzle == 'NNNcube':
            self.puzzleSize = size

            print('Creating scramble buffer...')   
            self.scrambler = CubeScramblerByRandomTurns(self.puzzleSize)
            self.scrambleBuffer = ScrambleBuffer(self.scrambler)
            print('Scramble buffer ready')
        
    
    def newSolve(self):
        '''
        Checks if there are enough scrambles in the scramble buffer. If not, then it generates new scrambles for the buffer.        
        '''
        print('Generating new scramble...')
        scramble = self.scrambleBuffer.getNextScramble()
        self.scrambleDisplay.setText(scramble)
        self.scrambleDisplay.resizeEvent()
        self.cubePicture.updateScramble(scramble)
        print('Ready.')
        

    def closeEvent(self, *args, **kwargs):
        '''
        Performs additional tasks before closing
        '''

        self.saveSettings()
        
        


class StretchyCenteredDisplay(QtGui.QLabel):
    '''
    A label with centred text that automatically resizes the font to fill the available space 
    '''

    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.setAlignment(Qt.AlignCenter)
        


    def resizeEvent(self, event):
        font = self.font()
        newSize = min(self.height() * magicHeightSizeFactor, self.width() / magicWidthSizeFactor)
        font.setPixelSize(newSize)
        self.setFont(font)
        

class ScrambleDisplay(QtGui.QLabel):

    def __init__(self, container, *args, **kwargs):
        self.container = container
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        

    def resizeEvent(self, event=None):
        
        QtGui.QLabel.resizeEvent(self, event)
        self.setMinimumHeight(1)
        self.setFixedHeight(self.heightForWidth(self.container.width()))
        
        

class TimerDisplay(StretchyCenteredDisplay):
    '''
    A StretchyCenteredDisplay with centred text that automatically resizes the font to fill the available space 
    '''

    def __init__(self, *args, **kwargs):
        StretchyCenteredDisplay.__init__(self, *args, **kwargs)

        font = self.font()
        font.setBold(True)
        self.setFont(font)
