#!/usr/bin/python3

STYLE_SHEET='''
color:rgb(0,0,0);
font-family: "DejaVu Sans Mono";
font-size: 14px;
'''

if __name__=='__main__':
    print('Import PyQt framework...',end='')
    try:
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        from PyQt5.QtWidgets import *
    except ImportError:
        print('faild.')
        print('Please check your Python and PyQt.The required version is Python3(CPython) and PyQt5 for Python3')
        import sys
        sys.exit(1)
    print('done.')
    print('Import XNBStream...',end='')
    from XNBStream import *
    print('done.')
else:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from XNBStream import *

class MainWindow(QMainWindow):
    
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.configWindow=ConfigWindow()
        self.configWindow.setWindowTitle('Settings')
        configWindowSize=self.configWindow.sizeHint()
        self.configWindow.setFixedSize(configWindowSize)
        self.configWindow.configChanged.connect(self.updateXNBConfigLabel)
        self.configWindow.configChanged.connect(self.contentChangedSlot)
        
        self.jumpWindow=JumpWindow()
        self.jumpWindow.setWindowTitle('Jump')
        jumpWindowSize=self.jumpWindow.sizeHint()
        self.jumpWindow.setFixedSize(jumpWindowSize)
        self.jumpWindow.jump.connect(self.jumpToLine)

        self.findWindow=FindWindow()
        self.findWindow.setWindowTitle('Find')
        findWindowSize=self.findWindow.sizeHint()
        self.findWindow.find.connect(self.findSlot)

        self.createMenus()
        self.createStatusBar()

        mainWidget=QWidget()
        rootLayout=QVBoxLayout()

        self.dataTextEdit=QTextEdit('')
        self.dataTextEdit.setWordWrapMode(QTextOption.NoWrap)
        self.dataTextEdit.cursorPositionChanged.connect(self.updateRuler)
        self.dataTextEdit.textChanged.connect(self.contentChangedSlot)
        self.dataTextEdit.setStyleSheet(STYLE_SHEET)
        rootLayout.addWidget(self.dataTextEdit)

        mainWidget.setLayout(rootLayout)
        self.setCentralWidget(mainWidget)

        self.updateRuler()
        self.updateXNBConfigLabel()

        self.dataTextEdit.setAcceptDrops(True)
        self.setAcceptDrops(True)

        self.currentFileName=''
        self.contentChanged=False

    
    def createMenus(self):
        fileMenu=self.menuBar().addMenu('&File')

        newAct=QAction('&New file',self)
        newAct.setShortcut(QKeySequence.New)
        newAct.triggered.connect(self.newFileSlot)

        openAct=QAction('&Open',self)
        openAct.setShortcuts(QKeySequence.Open)
        openAct.triggered.connect(self.openSlot)

        saveAct=QAction('&Save',self)
        saveAct.setShortcuts(QKeySequence.Save)
        saveAct.triggered.connect(self.saveSlot)

        saveAsAct=QAction('Save As',self)
        saveAsAct.triggered.connect(self.saveAsSlot)

        closeAct=QAction('&Close',self)
        closeAct.setShortcuts(QKeySequence.Close)
        closeAct.triggered.connect(self.close)

        fileMenu.addAction(newAct)
        fileMenu.addAction(openAct)
        fileMenu.addAction(saveAct)
        fileMenu.addAction(saveAsAct)
        fileMenu.addAction(closeAct)

        toolMenu=self.menuBar().addMenu('&Tool')
        configAct=QAction('&Settings',self)
        configAct.triggered.connect(self.configWindow.show)
        configAct.triggered.connect(self.configWindow.activateWindow)
        toolMenu.addAction(configAct)

        editMenu=self.menuBar().addMenu('&Edit')

        jumpAct=QAction('&Jump to',self)
        jumpAct.setShortcuts(QKeySequence('Ctrl+G'))
        jumpAct.triggered.connect(self.jumpWindow.show)
        jumpAct.triggered.connect(self.jumpWindow.activateWindow)
        jumpAct.triggered.connect(self.jumpWindow.dataLineEdit.setFocus)
        editMenu.addAction(jumpAct)

        findAct=QAction('&Find',self)
        findAct.setShortcuts(QKeySequence.Find)
        findAct.triggered.connect(self.findWindow.show)
        findAct.triggered.connect(self.findWindow.activateWindow)
        findAct.triggered.connect(self.findWindow.findWhatLineEdit.setFocus)
        editMenu.addAction(findAct)

    def createStatusBar(self):
        rulerLabel=QLabel()
        rulerLabel.setMinimumSize(rulerLabel.minimumSizeHint())
        rulerLabel.setAlignment(Qt.AlignHCenter)
        rulerLabel.setFrameShape(QFrame.WinPanel)
        XNBConfigLabel=QLabel()
        XNBConfigLabel.setMinimumSize(XNBConfigLabel.minimumSizeHint())
        XNBConfigLabel.setAlignment(Qt.AlignHCenter)
        XNBConfigLabel.setFrameShape(QFrame.WinPanel)
        self.statusBar().addWidget(rulerLabel)
        self.statusBar().addWidget(XNBConfigLabel)
        self.rulerLabel=rulerLabel
        self.XNBConfigLabel=XNBConfigLabel
    @pyqtSlot()
    def updateRuler(self):
        textCursor=self.dataTextEdit.textCursor()
        colNum=textCursor.positionInBlock()
        rowNum=textCursor.blockNumber()        
        self.rulerLabel.setText(str(colNum+1)+', '+str(rowNum+1))
    @pyqtSlot()
    def updateXNBConfigLabel(self):
        self.XNBConfigLabel.setText(repr(self.configWindow))

    def closeEvent(self,e):
        if self.contentChanged:
            result=QMessageBox.question(self,"XNB Editor","Save changes?",
                                 QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel),
                                 QMessageBox.Yes)
            if result==QMessageBox.Yes:
                self.saveFile(self.currentFileName)
            elif result==QMessageBox.Cancel:
                e.ignore()
                return
        self.configWindow.close()
        self.jumpWindow.close()
        self.findWindow.close()
    def dragEnterEvent(self,event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.acceptProposedAction()
    def dropEvent(self,event):
        urls=event.mimeData().urls()
        if len(urls)==0:
            return
        fileName=urls[0].toLocalFile()
        if fileName=='':
            return
        if self.contentChanged:
            result=QMessageBox.question(self,"XNB Editor","Save changes?",
                                 QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel),
                                 QMessageBox.Yes)
            if result==QMessageBox.Yes:
                self.saveFile(self.currentFileName)
            elif result==QMessageBox.Cancel:
                return
        self.openFile(fileName)
        self.currentFileName=fileName
        self.contentChanged=False

    def openFile(self,fileName):
        if fileName.endswith('.xnb'):
            f=open(fileName,'rb')
            try:
                targetPlatform,readerName,text=readXNB(f)
            except XNBFormatException as e:
                QMessageBox.warning(self,'XNB Editor','Cannot open the XNB file.')
                if __name__=='__main__':
                    print('failed to load file: '+e.description)
                f.close()
                return
            f.close()
            self.configWindow.setConfig(targetPlatform,readerName)
        elif fileName.endswith('.xml') or fileName.endswith('.txt'):
            f=open(fileName,'r')
            text=f.read()
            f.close()
        else:
            return
        self.dataTextEdit.setText(text)
    def saveFile(self,fileName):
        if fileName.endswith('.xnb'):
            targetPlatform,readerName=self.configWindow.getConfig()
            f=open(fileName,'wb')
            writeXNB(f,targetPlatform,readerName,self.dataTextEdit.toPlainText())
            f.close()
        elif fileName.endswith('.xml') or fileName.endswith('.txt'):
            f=open(fileName,'w')
            f.write(self.dataTextEdit.toPlainText())
            f.close()

    @pyqtSlot()
    def newFileSlot(self):
        if self.contentChanged:
            result=QMessageBox.question(self,"XNB Editor","Save changes?",
                                 QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel),
                                 QMessageBox.Yes)
            if result==QMessageBox.Yes:
                self.saveFile(self.currentFileName)
            elif result==QMessageBox.Cancel:
                return
        self.dataTextEdit.setText('')
        self.currentFileName=''
        self.contentChanged=False
    @pyqtSlot()
    def openSlot(self):
        if self.contentChanged:
            result=QMessageBox.question(self,"XNB Editor","Save changes?",
                                 QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel),
                                 QMessageBox.Yes)
            if result==QMessageBox.Yes:
                self.saveFile(self.currentFileName)
            elif result==QMessageBox.Cancel:
                return
        fileName=QFileDialog.getOpenFileName(self,
                'Open File',
                '.',
                'Survivalcraft XNB files (*.xnb);;XML files (*.xml);;Text files(*.txt)')[0]
        self.openFile(fileName)
        self.currentFileName=fileName
        self.contentChanged=False
    @pyqtSlot()
    def saveSlot(self):
        if self.currentFileName=='':
            fileName=QFileDialog.getSaveFileName(self,
                    'Save File',
                    '.',
                    'Survivalcraft XNB files (*.xnb);;XML files (*.xml);;Text files(*.txt)')[0]
            self.currentFileName=fileName
        else:
            fileName=self.currentFileName
        self.saveFile(fileName)
        self.contentChanged=False
    @pyqtSlot()
    def saveAsSlot(self):
        fileName=QFileDialog.getSaveFileName(self,
                'Save File',
                '.',
                'Survivalcraft XNB files (*.xnb);;XML files (*.xml);;Text files(*.txt)')[0]
        self.saveFile(fileName)

    @pyqtSlot(int)
    def jumpToLine(self,lineNumber):
        textCursor=self.dataTextEdit.textCursor()
        position=self.dataTextEdit.document().findBlockByNumber(lineNumber-1).position()
        textCursor.setPosition(position,QTextCursor.MoveAnchor)
        self.dataTextEdit.setTextCursor(textCursor)
        self.jumpWindow.hide()

    @pyqtSlot(str,QTextDocument.FindFlags)
    def findSlot(self,findWhat,flags):
        result=self.dataTextEdit.find(QRegExp(findWhat),flags)
        self.activateWindow()

    def chechXML(self):
        from xml.dom.minidom import parseString
        text=self.dataTextEdit.toPlainText()
        try:
            parseString(text)
        except:
            return False
        return True

    @pyqtSlot()
    def contentChangedSlot(self):
        self.contentChanged=True


class ConfigWindow(QWidget):
    configChanged=pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        rootLayout=QVBoxLayout()

        formLayout=QFormLayout()

        comboTarget=QComboBox()
        comboTarget.addItem('Android/IOS')
        comboTarget.addItem('Windows Phone')
        comboTarget.setCurrentIndex(0)
        comboTarget.currentIndexChanged.connect(self.configChanged)
        formLayout.addRow('&Target',comboTarget)
        self.comboTarget=comboTarget

        comboTypeReader=QComboBox()
        comboTypeReader.addItem('String')
        comboTypeReader.addItem('XElement')
        comboTypeReader.setCurrentIndex(0)
        comboTypeReader.currentIndexChanged.connect(self.configChanged)
        formLayout.addRow('Type &Reader',comboTypeReader)
        self.comboTypeReader=comboTypeReader

        okButton=QPushButton('&OK')
        okButton.clicked.connect(self.hide)

        rootLayout.addLayout(formLayout)
        rootLayout.addWidget(okButton)

        self.setLayout(rootLayout)

    def getConfig(self):
        config=[]
        if self.comboTarget.currentIndex()==0:
            config.append(b'w')
        elif self.comboTarget.currentIndex()==1:
            config.append(b'm')
        else:
            config.append(None)
        if self.comboTypeReader.currentIndex()==0:
            config.append('Microsoft.Xna.Framework.Content.StringReader')
        elif self.comboTypeReader.currentIndex()==1:
            config.append('Game.XElementReader, Game')
        else:
            config.append(None)
        return config

    def setConfig(self,targetPlatform,readerName):
        if targetPlatform==b'w':
            self.comboTarget.setCurrentIndex(0)
        elif targetPlatform==b'm':
            self.comboTarget.setCurrentIndex(1)
        if readerName=='Microsoft.Xna.Framework.Content.StringReader':
            self.comboTypeReader.setCurrentIndex(0)
        elif readerName=='Game.XElementReader, Game':
            self.comboTypeReader.setCurrentIndex(1)

    def __repr__(self):
        return self.comboTarget.currentText()+' | '+self.comboTypeReader.currentText()


class JumpWindow(QWidget):

    jump=pyqtSignal(int)

    def __init__(self):
        QWidget.__init__(self)
        
        rootLayout=QVBoxLayout()

        rootLayout.addWidget(QLabel('Line number: '))
        
        self.dataLineEdit=QLineEdit()
        self.dataLineEdit.returnPressed.connect(self.jumpSlot)
        rootLayout.addWidget(self.dataLineEdit)

        buttonLayout=QHBoxLayout()

        buttonJump=QPushButton('&Jump')
        buttonJump.clicked.connect(self.jumpSlot)
        buttonLayout.addWidget(buttonJump)

        buttonCancel=QPushButton('&Cancel')
        buttonCancel.clicked.connect(self.hide)
        buttonLayout.addWidget(buttonJump)

        rootLayout.addLayout(buttonLayout)

        self.setLayout(rootLayout)

    @pyqtSlot()
    def jumpSlot(self):
        lineNumber=int(self.dataLineEdit.text())
        self.jump.emit(lineNumber)


class FindWindow(QWidget):

    find=pyqtSignal(str,QTextDocument.FindFlags)

    def __init__(self):
        QWidget.__init__(self)
        
        rootLayout=QHBoxLayout()

        contentLayout=QVBoxLayout()# start of contentLayout
        
        findWhatLayout=QHBoxLayout()
        findWhatLayout.addWidget(QLabel('Find what? '))
        self.findWhatLineEdit=QLineEdit()
        self.findWhatLineEdit.returnPressed.connect(self.findSlot)
        findWhatLayout.addWidget(self.findWhatLineEdit)

        flagLayout=QHBoxLayout()# start of flagLayout

        directionGroup=QGroupBox('Direction: ')
        directionLayout=QHBoxLayout()
        self.backawardRadioButton=QRadioButton('&Backaward')
        self.forawardRadioButton=QRadioButton('&Foraward')
        self.forawardRadioButton.setChecked(True)
        # self.backawardRadioButton.setChecked(False)
        directionLayout.addWidget(self.backawardRadioButton)
        directionLayout.addWidget(self.forawardRadioButton)
        directionLayout.addStretch()
        directionGroup.setLayout(directionLayout)

        self.caseCheckBox=QCheckBox('&CaseSensitive')
        self.caseCheckBox.setChecked(False)
        
        flagLayout.addWidget(self.caseCheckBox)
        flagLayout.addWidget(directionGroup)# end of flagLayout

        contentLayout.addLayout(findWhatLayout)
        contentLayout.addLayout(flagLayout)# end of contentLayout

        buttonLayout=QVBoxLayout()# start of buttonLayout
        buttonFind=QPushButton('&Find')
        buttonFind.clicked.connect(self.findSlot)
        buttonCancel=QPushButton('Cancel')
        buttonCancel.clicked.connect(self.close)
        buttonLayout.addWidget(buttonFind)
        buttonLayout.addWidget(buttonCancel)# end of buttonLayout
        
        rootLayout.addLayout(contentLayout)
        rootLayout.addLayout(buttonLayout)

        self.setLayout(rootLayout)

    @pyqtSlot()
    def findSlot(self):
        flags=QTextDocument.FindFlag()
        if self.backawardRadioButton.isChecked():
            flags|=QTextDocument.FindBackward
        if self.caseCheckBox.isChecked():
            flags|=QTextDocument.FindCaseSensitively
        findWhat=self.findWhatLineEdit.text()
        self.find.emit(findWhat,flags)


def main():
    import sys
    a=QApplication(sys.argv)
    print('Create main window...',end='')
    mainwindow=MainWindow()
    mainwindow.setWindowTitle('XNB Editor')
    mainwindow.resize(800,600)
    if len(sys.argv)>=2:
        mainwindow.openFile(sys.argv[1])
        mainwindow.currentFileName=sys.argv[1]
    print('done.')
    mainwindow.show()
    print('Main window showed up.')
    sys.exit(a.exec())

if __name__=='__main__':
    main()

