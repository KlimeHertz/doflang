from PyQt5.QtCore import pyqtSlot, QObject , pyqtSignal
import time
from helper import HarvestType
import threading
from helper import ressourceStatus
import globalstore

class scriptRunner(QObject):
    moveToCell = pyqtSignal(int)
    moveToPosition = pyqtSignal(int, int)
    clickPosition = pyqtSignal(int, int)
    harvest = pyqtSignal(int, HarvestType)
    scirptError = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.allLines = list()
        self.statements = dict()
        self.timers = dict()
        self.currentLine = 0
        self.scriptName = ""
        self.Looping = True
        self.stoped = False
        self.scriptVariables = dict()
        self.timerruning = False
            
    @pyqtSlot(str)     
    def loadScript(self, path):
        if not path.lower().endswith('.scp'):
            print("Invalid file extension. Only '.scp' files are allowed.")
            return
        
        self.Looping = True
        self.stoped = False
        
        with open(path, 'r') as file:
            self.allLines = file.read()
            self.allLines = self.allLines.split(';')            
            
        lineNumber = 1
        for line in self.allLines:            
            line = line.strip()
            if line:
                try:
                    stmts=line.split(' ')
                    if stmts:
                        self.statements[str(lineNumber)] = stmts
                except Exception as e:
                    print(f"Could not split Line {lineNumber}: {e}")
            lineNumber += 1
            
        print(f"Script loaded with {self.statements} statements.")
        self.runScript()
        
    @pyqtSlot(str)
    def executeCombatEnd(self, withLevelUp):
        """At the end of a combat we need to click on ok and then on the level up if we have one.
        parametes:
        withLevelUp: boolean, true if we have a level up, false otherwise.
        """
        self.stoped = True
        
        
            
    @pyqtSlot()
    def stopRunningScript(self):
        self.stoped = True
        
    @pyqtSlot()
    def resumeRunningScript(self):
        self.stoped = False
        self.runScript(self.currentLine)
        
    def runStatementAtLine(self, lineId):
        if str(lineId) in self.statements.keys():
            statement = self.statements[str(lineId)]
            try:
                if statement[0] == 'moveToCell':
                    self.moveToCell.emit(int(statement[1]))
                elif statement[0] == 'setLooping':
                    if statement[1] == 'true':
                        self.Looping = True
                    else:
                        self.Looping = False
                elif statement[0] == 'moveToPosition':
                    self.moveToPosition.emit(int(statement[1]), int(statement[2]))
                elif statement[0] == 'clickPosition':
                    self.clickPosition.emit(int(statement[1]), int(statement[2]))
                elif statement[0] == 'harvest':
                    #check if harvestable
                    if globalstore.store.harvestableTiles[int(statement[1])] == ressourceStatus.SPAWNED:                        
                        self.harvest.emit(int(statement[1]), HarvestType.CLICKONLVL1)
                elif statement[0] == 'waitInSeconds':
                    time.sleep(int(statement[1]))
                elif statement[0] == 'changeMap':
                    pass
                elif statement[0] == 'stop':
                    self.stoped = True
                elif statement[0] == 'defineVar':
                    #defineVar varName varType varValue
                    #varType: int, str, bool
                    if not statement[1] or not statement[2] or not statement[3]:
                        raise ValueError("Variable name or value is missing.")
                    else:
                        variableName = statement[1]
                        variablType = statement[2]
                        variableValue = statement[3]
                        self.scriptVariables[variableName] = (variablType,variableValue)
                elif statement[0] == 'changeVar':
                    if not statement[1] or not statement[2]:
                        raise ValueError("Variable name or value is missing.")
                    else:
                        variableName = statement[1]
                        variableNewValue = statement[2]
                        if variableName in self.scriptVariables.keys():
                            self.scriptVariables[variableName] = (self.scriptVariables[variableName][0], variableNewValue)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifEqualTest':
                    #ifEqualTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = statement[2]
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if self.scriptVariables[variableName][1] == testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifNotEqualTest':
                    #ifNotEqualTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = statement[2]
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if self.scriptVariables[variableName][1] != testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifGreaterTest':
                    #ifGreaterTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = int(statement[2])
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if int(self.scriptVariables[variableName][1]) > testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifLessTest':
                    #ifLessTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = int(statement[2])
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if int(self.scriptVariables[variableName][1]) < testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifGreaterEqualTest':
                    #ifGreaterEqualTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = int(statement[2])
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if int(self.scriptVariables[variableName][1]) >= testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == 'ifLessEqualTest':
                    #ifLessEqualTest varName testValue lineIfTrue lineIfFalse
                    if not statement[1] or not statement[2] or not statement[3] or not statement[4]:                        
                        raise ValueError("Test condition or value is missing.")
                    else:
                        variableName = statement[1]
                        testValue = int(statement[2])
                        lineIfTrue = statement[3]
                        lineIfFalse = statement[4]
                        
                        if variableName in self.scriptVariables.keys():
                            if int(self.scriptVariables[variableName][1]) <= testValue:
                                self.currentLine = int(lineIfTrue)
                                self.runStatementAtLine(self.currentLine)
                            else:
                                self.currentLine = int(lineIfFalse)
                                self.runStatementAtLine(self.currentLine)
                        else:
                            raise ValueError(f"Variable {variableName} does not exist.")
                elif statement[0] == "startWatch":                    
                    #startWatch timername duration lineToExecuteAfter
                    def timerDoneCounting(timerid):
                        timer = self.timers[timerid]
                        print("Timer finished. Performing scheduled action.")
                        self.currentLine = timer[1]
                        self.runStatementAtLine(self.currentLine)
                        
                    if not statement[1] or not statement[3] or not statement[2] or float(statement[1]) <= 0:
                        raise ValueError("Timer duration is missing or negative.")
                    else:
                        timerId = statement[2]                                 
                        self.timers[timerId] = (threading.Timer(float(statement[2]), timerDoneCounting, statement[1]), statement[3])
                        self.timers[timerId].start()
                elif statement[0] == "goto":
                    #goto lineId
                    if not statement[1]:
                        raise ValueError("Line ID is missing.")
                    else:
                        self.currentLine = int(statement[1])
                        self.runStatementAtLine(self.currentLine)
                else:
                    print(f"Unknown command: {statement[0]}")
                    raise ValueError(f"Unknown command: {statement[0]}")                                                                                                                                                                                       
            except Exception as e:
                self.stoped = True
                self.scirptError.emit(f"Error executing line {lineId}: {e}") 
                raise ValueError(f"Error executing line {lineId}: {e}")
        else:                 
            self.stoped = True
            self.scirptError.emit(f"Line {lineId} not found in script.")   
            raise ValueError(f"Line {lineId} not found in script.")         
        
                
    @pyqtSlot()   
    def runScript(self,startLine=1):
        self.currentLine = startLine
        looping = self.Looping
        while (looping):
            if self.stoped:
                break
            else:
                try:
                    if self.currentLine > len(self.statements):
                        if self.Looping:
                            self.currentLine = 1
                        else:
                            break
                    self.runStatementAtLine(self.currentLine)            
                    self.currentLine = self.currentLine + 1
                except Exception as e:
                    print(f"Error executing line {self.currentLine}: {e}")
            
            