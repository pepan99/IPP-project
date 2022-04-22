import argparse
import sys
from enum import Enum
import xml.etree.ElementTree as ET
import re
'''
// ENUM of error types
/////////////////////////////////////////////////////////////////////////////'''
class ErrorTypes(Enum):
    ERR_ARGUMENT_COMB = 10
    ERR_OUTPUT_FILE = 11
    ERR_INPUT_FILE = 12
    ERR_XML_FORMAT = 31
    ERR_XML_STRUCTURE = 32
    ERR_SEMANTIC = 52
    ERR_OPERAND_TYPE = 53
    ERR_NONEXIST_VAR = 54
    ERR_NONEXIST_FRAME = 55
    ERR_MISSING_VAL = 56
    ERR_WRONG_OP_VAL = 57
    ERR_STRING = 58

'''
// error handling based on error number
/////////////////////////////////////////////////////////////////////////////'''
def errorHandling(errorNumber):
    if (errorNumber == ErrorTypes.ERR_ARGUMENT_COMB):
        print('Wrong argument combination/invalid arguments.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_OUTPUT_FILE):
        print('Error opening output file.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_INPUT_FILE):
        print('Error opening input file.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_XML_FORMAT):
        print('Error in XML formatting.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_XML_STRUCTURE):
        print('Unexpected XML formatting or lexical/syntactic error in elements/attributes.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_SEMANTIC):
        print('Semantic error of input IPPcode21 code.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_OPERAND_TYPE):
        print('Wrong operand type.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_NONEXIST_VAR):
        print('Non existing variable.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_NONEXIST_FRAME):
        print('Non existing frame.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_MISSING_VAL):
        print('Missing value.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_WRONG_OP_VAL):
        print('Wrong operand value.', file=sys.stderr)
        sys.exit(errorNumber.value)
    elif (errorNumber == ErrorTypes.ERR_STRING):
        print('String error.', file=sys.stderr)
        sys.exit(errorNumber.value)
'''
// CLASS FOR XML PARSING
/////////////////////////////////////////////////////////////////////////////'''
class ParseXML():
    # tree and inputFile should be already read from file and now further parsed
    def __init__(self, tree, inputFile):
        self.tree = tree
        self.inputFile = inputFile
        self.child = ''
        self.dictionary = ''
        self.instructionNum = 0
        try:
            self.root = tree.getroot()
        except:
            errorHandling(ErrorTypes.ERR_XML_FORMAT)
    
    def main(self):
        self.checkHeader()
        self.checkInstruction()
        # checks opcode, order and arguments and puts instruction into a list
        self.createInstructionList()
    
    def checkHeader(self):
        if not (self.root.tag == 'program'):
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        elif not (self.root.attrib['language'] == 'IPPcode21'):
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        
    def checkInstruction(self):
        count = 0
        for child in self.root:
            if not (child.tag == 'instruction'):
                errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
            count += 1
        self.dictionary = [dict() for x in range(count)]
    
    def createInstructionList(self):
        for child in self.root:
            self.child = child
            try:
                orderNum = int(child.attrib["order"])
            except:
                errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
            if (orderNum < 1):
                errorHandling(ErrorTypes.ERR_XML_FORMAT)
            self.dictionary[self.instructionNum]["order"] = orderNum
            
            self.checkOpcode()
            self.instructionNum += 1

    def checkOpcode(self):
        vVar = 'var'
        vSymb = 'symb'
        vLabel = 'label'
        vType = 'type' 
        vNone = 'none'
        try:
            opcode = str(self.child.attrib["opcode"]).upper()
            self.dictionary[self.instructionNum]["opcode"] = opcode
        except:
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        if (opcode in ['RETURN', 'BREAK', 
            'CREATEFRAME', 'PUSHFRAME', 'POPFRAME']):
            self.checkArguments(0, vNone, vNone, vNone)
        elif (opcode in ['DEFVAR', 'POPS']):
            self.checkArguments(1, vVar, vNone, vNone)
        elif (opcode in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']):
            self.checkArguments(1, vSymb, vNone, vNone)
        elif (opcode in ['LABEL', 'JUMP', 'CALL']):
            self.checkArguments(1, vLabel, vNone, vNone)
        elif (opcode in ['MOVE', 'INT2CHAR',
            'STRLEN', 'NOT', 'TYPE']):
            self.checkArguments(2, vVar, vSymb, vNone)
        elif (opcode == 'READ'):
            self.checkArguments(2, vVar, vType, vNone)
        elif (opcode in ['ADD', 'SUB',
            'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 
            'OR', 'STRI2INT', 'CONCAT', 'GETCHAR','SETCHAR']):
            self.checkArguments(3, vVar, vSymb, vSymb)
        elif (opcode in ['JUMPIFEQ', 'JUMPIFNEQ']):
            self.checkArguments(3, vLabel, vSymb, vSymb)
        else:
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)

    def checkArguments(self, numberOf, type1, type2, type3):
        argnum = 0
        for argument in self.child:
            argnum += 1
            if (argument.tag in ['arg1', 'arg2', 'arg3']):
                if (argument.attrib["type"] in ['string', 'int', 'nil', 'var', 'bool', 'label', 'type']):
                    self.dictionary[self.instructionNum][argument.tag] = argument.attrib["type"]
                    self.dictionary[self.instructionNum][argument.tag + 'Val'] = argument.text
            else:
                errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        
        if (type1 == 'var'):
            self.checkVar(1)
        elif (type1 == 'symb'):
            self.checkSymb(1)
        elif (type1 == 'label'):
            self.checkLabel(1)
        if (type2 == 'symb'):
            self.checkSymb(2)
        elif (type2 == 'type'):
            self.checkType(2)
        if (type3 == 'symb'):
            self.checkSymb(3)
        if not (argnum == numberOf):
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)

    def checkVar(self, numOfArg):
        try:
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'var'
        except:
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        return

    def checkSymb(self, numOfArg):
        try:    
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'var' 
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'int' 
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'string' 
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'bool' 
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'nil'
        except:    
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        return

    def checkLabel(self, numOfArg):
        try: 
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'label'
        except:    
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        return

    def checkType(self, numOfArg):
        try:
            self.dictionary[self.instructionNum]["arg"+str(numOfArg)] == 'type'
        except:
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        return

'''/////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// CLASS FOR ARGUMENT PARSING, TREE CREATING, READING INPUT FILE
/////////////////////////////////////////////////////////////////////////////'''

class ParseArguments():
# initializes fields
    def __init__(self):
        self.inputFile = ''
        self.tree = ''
        self.root = ''

# calls other methods 
    def main(self):
        self.parseArgs()
        self.sourceParse()
        self.inputParse()

# parses arguments, checks combinations
    def parseArgs(self):
        parser = argparse.ArgumentParser(description='Interpret XML representation of IPPcode21', add_help=False)
        parser.add_argument('--help', dest='help',action='store_true', help='Usage: python3.8 interpret.py --source= file and, or --input= file')
        parser.add_argument('--source=', dest='source', help='XML source file')
        parser.add_argument('--input=', dest='input', help='Input files for interpretation')
        
        try:
            self.parse = parser.parse_args()
        except SystemExit:
            errorHandling(ErrorTypes.ERR_ARGUMENT_COMB)
        
        if (self.parse.help):
            if(self.parse.source or self.parse.input):
                errorHandling(ErrorTypes.ERR_ARGUMENT_COMB)
            else:
                parser.print_help()
                sys.exit(0)
        else:
            if not (self.parse.source or self.parse.input):
                errorHandling(ErrorTypes.ERR_ARGUMENT_COMB)

# parses source file with XML representation if argument is added
# else reads from stdin
    def sourceParse(self):
        try:
            if (self.parse.source):
                self.tree = ET.parse(self.parse.source)
            else:
                self.tree = ET.parse(sys.stdin)

            self.root = self.tree.getroot()
        except ET.ParseError:
            errorHandling(ErrorTypes.ERR_XML_FORMAT)
# parses input file for code interpretation if argument is added
# else reads from stdin
    def inputParse(self):
        try:
            if (self.parse.input):
                f = open(self.parse.input, "r")
                self.inputFile = f.readlines()
                self.inputFile.sort(reverse=True)
                f.close()
            else: 
                self.inputFile = sys.stdin.readlines()
        except:
            errorHandling(ErrorTypes.ERR_ARGUMENT_COMB)
        

'''/////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////'''
'''
// LABELS, INSTRUCTION STACK, FRAMES
/////////////////////////////////////////////////////////////////////////////'''
#
class Labels():
    def __init__(self):
        self.labels = {}

    def pushLabel(self, label, instrCounter):
        label = str(label)
        if (label in self.labels):
            errorHandling(ErrorTypes.ERR_SEMANTIC)
        else:
            self.labels[label] = instrCounter
        
    def jumpToLabel(self, label, instrCounter):
        label = str(label)
        if (label in self.labels):
            instrCounter = self.labels[label]
        else:
            errorHandling(ErrorTypes.ERR_SEMANTIC)

class InstructionStack():
    def __init__(self):
        self.values = []
        
    def popFromStack(self):
        if not (len(self.values) == 0):
            return self.values.pop()
        else:
            errorHandling(ErrorTypes.ERR_MISSING_VAL)
        
    def pushToStack(self, value):
        self.values.append(value)
    
    

class Frames():
    def __init__(self):
        self.localFrame = []
        self.tempFrameDef = False
        self.tempFrame = {}
        self.globalFrame = {}
        
    def createFrame(self):
        self.tempFrameDef = True
        self.tempFrame = {}
        return
    
    def pushFrame(self):
        if (self.tempFrameDef == True):
            self.localFrame.append(self.tempFrame)
            self.tempFrameDef = False
        else:
            errorHandling(ErrorTypes.ERR_NONEXIST_FRAME)
    
    def popFrame(self):
        if (len(self.localFrame) > 0):
            self.tempFrame = self.localFrame.pop()
            self.tempFrameDef = True
        else: 
            errorHandling(ErrorTypes.ERR_NONEXIST_FRAME)
        return

    def getFrame(self, frame):
        if (frame == 'TF' and self.tempFrameDef):
            return self.tempFrame
        elif (frame == 'LF' and len(self.localFrame) > 0):
            return self.localFrame[len(self.localFrame)-1]
        elif (frame == 'GF'):
            return self.globalFrame
        else: return 'NOTDEF'

    def defVariable(self, value):
        value = value.split('@', 1)
        frame = self.getFrame(value[0])
        if (frame == 'NOTDEF'):
            errorHandling(ErrorTypes.ERR_NONEXIST_FRAME)
        elif (value[1] in frame):
            errorHandling(ErrorTypes.ERR_SEMANTIC)
        else: frame[value[1]] = {"data": None, "type": None}
        return
    
    def setVariable(self, value, type1, data):
        value = value.split('@', 1)
        frame = self.getFrame(value[0])
        if (frame == 'NOTDEF'):
            errorHandling(ErrorTypes.ERR_NONEXIST_FRAME)
        elif not (value[1] in frame):
            errorHandling(ErrorTypes.ERR_NONEXIST_VAR)
        else:
            frame[value[1]]["type"] = type1
            frame[value[1]]["data"] = data
        return

    def getVariable(self, value):
        value = value.split('@', 1)
        frame = self.getFrame(value[0])
        if (frame == 'NOTDEF'):
            errorHandling(ErrorTypes.ERR_NONEXIST_FRAME)
        elif not (value[1] in frame):
            errorHandling(ErrorTypes.ERR_NONEXIST_VAR)
        else: return (frame[value[1]])
        
    def getValue(self, variable):
        return self.getVariable(variable)
'''
// INSTRUCTION CLASS
/////////////////////////////////////////////////////////////////////////////'''
class ParseInstructions():
    def __init__(self, dictionary, checkedXML, inputFile):
        self.dictionary = dictionary
        self.instruction = ''
        self.checkedXML = checkedXML
        self.inputFile = inputFile
        self.callStack = InstructionStack()
        self.dataStack = InstructionStack()
        self.labels = Labels()
        self.frame = Frames()
        self.instrCounter = 0

    def main(self):
        self.getLabels()
        while(self.instrCounter < checkedXML.instructionNum):
            self.instruction = self.dictionary[self.instrCounter]
            self.checkInstrLogic()
            self.instrCounter += 1
    
    def getLabels(self):
        for instruction in self.dictionary:
            if (instruction["opcode"] == 'LABEL'):
                self.labels.pushLabel(instruction["arg1Val"], instruction["order"])
    
    def returnDataType(self, instrNum):
        instrNum = str(instrNum)
        if (self.instruction["arg" + instrNum] == 'var'):
            varVal = self.frame.getValue(self.instruction["arg"+instrNum+"Val"])
            #varVal["data"] varVal["type"]
            valueOf = varVal["data"]
            typeOf = varVal["type"]
            if (valueOf == None and typeOf == None and self.instruction["opcode"] != 'TYPE'):
                errorHandling(ErrorTypes.ERR_MISSING_VAL)
        else:
            valueOf = self.instruction["arg"+instrNum+"Val"]
            typeOf = self.instruction["arg"+instrNum]
        
        return valueOf, typeOf
    
    def checkRepairString(self, repairedString):
        escapeSeq = re.compile(r'\\(\d{1,3}')
        return escapeSeq.sub(chr(int(escapeSeq.group(1))), repairedString)
    
    def checkInstrLogic(self):
        if (self.instruction["opcode"] == 'RETURN'):
            self.__RETURN()
        elif (self.instruction["opcode"] == 'BREAK'):
            self.__BREAK()
        elif (self.instruction["opcode"] == 'CREATEFRAME'):
            self.__CREATEFRAME()
        elif (self.instruction["opcode"] == 'PUSHFRAME'):
            self.__PUSHFRAME()
        elif (self.instruction["opcode"] == 'POPFRAME'):
            self.__POPFRAME()
        elif (self.instruction["opcode"] == 'DEFVAR'):
            self.__DEFVAR()
        elif (self.instruction["opcode"] == 'POPS'):
            self.__POPS()
        elif (self.instruction["opcode"] == 'PUSHS'):
            self.__PUSHS()
        elif (self.instruction["opcode"] == 'WRITE'):
            self.__WRITE()
        elif (self.instruction["opcode"] == 'EXIT'):
            self.__EXIT()
        elif (self.instruction["opcode"] == 'DPRINT'):
            self.__DPRINT()
        elif (self.instruction["opcode"] == 'LABEL'):
            self.__LABEL()
        elif (self.instruction["opcode"] == 'JUMP'):
            self.__JUMP()
        elif (self.instruction["opcode"] == 'CALL'):
            self.__CALL()
        elif (self.instruction["opcode"] == 'MOVE'):
            self.__MOVE()
        elif (self.instruction["opcode"] == 'INT2CHAR'):
            self.__INT2CHAR()
        elif (self.instruction["opcode"] == 'STRLEN'):
            self.__STRLEN()
        elif (self.instruction["opcode"] == 'NOT'):
            self.__NOT()
        elif (self.instruction["opcode"] == 'TYPE'):
            self.__TYPE()
        elif (self.instruction["opcode"] == 'READ'):
            self.__READ()
        elif (self.instruction["opcode"] == 'ADD'):
            self.__ADD()
        elif (self.instruction["opcode"] == 'SUB'):
            self.__SUB()
        elif (self.instruction["opcode"] == 'MUL'):
            self.__MUL()
        elif (self.instruction["opcode"] == 'IDIV'):
            self.__IDIV()
        elif (self.instruction["opcode"] == 'LT'):
            self.__LT()
        elif (self.instruction["opcode"] == 'GT'):
            self.__GT()
        elif (self.instruction["opcode"] == 'EQ'):
            self.__EQ()
        elif (self.instruction["opcode"] == 'AND'):
            self.__AND()
        elif (self.instruction["opcode"] == 'OR'):
            self.__OR()
        elif (self.instruction["opcode"] == 'STRI2INT'):
            self.__STRI2INT()
        elif (self.instruction["opcode"] == 'CONCAT'):
            self.__CONCAT()
        elif (self.instruction["opcode"] == 'GETCHAR'):
            self.__GETCHAR()
        elif (self.instruction["opcode"] == 'SETCHAR'):
            self.__SETCHAR()
        elif (self.instruction["opcode"] == 'JUMPIFEQ'):
            self.__JUMPIFEQ()
        elif (self.instruction["opcode"] == 'JUMPIFNEQ'):
            self.__JUMPIFNEQ()
        return

    # NO ARGS
    def __RETURN(self):
        self.instrCounter = self.callStack.popFromStack()
        return
    def __BREAK(self):
        pass
    def __CREATEFRAME(self):
        self.frame.createFrame()
        return
    def __PUSHFRAME(self):
        self.frame.pushFrame()
        return
    def __POPFRAME(self):
        self.frame.popFrame()
        return
    
    # ONE ARG 
    # var
    def __DEFVAR(self):
        self.frame.defVariable(self.instruction["arg1Val"])
        return
    def __POPS(self):
        value = self.dataStack.popFromStack()
        self.frame.setVariable(value, self.instruction["arg1"], self.instruction["arg1Val"])
        return
    
    # symb
    def __PUSHS(self):
        self.dataStack.pushToStack(self.instruction["arg1Val"])
        return
    def __WRITE(self):
        dataOf, typeOf = self.returnDataType(1)
        if (typeOf == 'str'):
            dataOf = self.checkRepairString(dataOf)
        if (dataOf == None):
            errorHandling(ErrorTypes.ERR_MISSING_VAL)
        if (typeOf  == 'nil'):
            print('', end='')
        else:
            print(dataOf, end='')
        return
    def __EXIT(self):
        dataOf, typeOf = self.returnDataType(1)
        if (typeOf == 'int'):
            try:
                retVal = int(dataOf)
                
            except:
                errorHandling(ErrorTypes.ERR_WRONG_OP_VAL)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        if (retVal < 0 or retVal > 49):
            errorHandling(ErrorTypes.ERR_WRONG_OP_VAL)
        exit(retVal)
    def __DPRINT(self):
        pass
    
    # label
    def __LABEL(self):
        pass
    def __JUMP(self):
        self.labels.jumpToLabel(self.instruction["arg1Val"], self.instrCounter)
        return
    def __CALL(self):
        self.callStack.pushToStack(self.instrCounter+1)
        self.labels.jumpToLabel(self.instruction["arg1Val"], self.instrCounter)
        return
    
    # TWO ARGS
    # var symb
    def __MOVE(self):
        self.frame.setVariable(self.instruction["arg1Val"], self.instruction["arg2"], self.instruction["arg2Val"])
        return
    def __INT2CHAR(self):
        dataOf, typeOf = self.returnDataType(2)
        if (typeOf == 'int'):    
            try:
                argVal = chr(int(dataOf))
            except:
                errorHandling(ErrorTypes.ERR_STRING)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        self.frame.setVariable(self.instruction["arg1Val"], typeOf, argVal)
        return
    def __STRLEN(self):
        dataOf, typeOf = self.returnDataType(2)
        if (typeOf == 'string'):
                strLen = len(dataOf)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        self.frame.setVariable(self.instruction["arg1Val"], typeOf, strLen)
        return
    def __NOT(self):
        dataOf, typeOf = self.returnDataType(2)
        if (typeOf == 'bool'):
                boolVal = not dataOf
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        self.frame.setVariable(self.instruction["arg1Val"], typeOf, boolVal)
        return
    def __TYPE(self):
        dataOf, typeOf = self.returnDataType(2)
        if (typeOf == None):
            typeOf = ''
        self.frame.setVariable(self.instruction["arg1Val"], typeOf, dataOf)
        return
    
    # var type
    def __READ(self):
        line = self.inputFile.pop()
        if (line == ''):
            typeOf = 'nil'
            dataOf = 'nil'
        elif (self.instruction["arg2"] == 'bool'):
            typeOf = 'bool'
            if (line == 'true'):
                dataOf = 'true'
            else:
                dataOf = 'false'
        else:
            typeOf = 'string'
            dataOf = line
        self.frame.setVariable(self.instruction["arg1Val"], typeOf, dataOf)
        return
    
    # THREE ARGS
    # var symb symb 
    def __ADD(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        if (typeOf2 == 'int' and typeOf3 == 'int'):
            try:
                dataOf2 = int(dataOf2)
                dataOf3 = int(dataOf3)
                result = dataOf2+dataOf3
            except:
                errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        
        self.frame.setVariable(self.instruction["arg1Val"], typeOf2, result)
        return
    def __SUB(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        if (typeOf2 == 'int' and typeOf3 == 'int'):
            try:
                dataOf2 = int(dataOf2)
                dataOf3 = int(dataOf3)
                result = dataOf2-dataOf3
            except:
                errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        
        self.frame.setVariable(self.instruction["arg1Val"], typeOf2, result)
        return
    def __MUL(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        if (typeOf2 == 'int' and typeOf3 == 'int'):
            try:
                dataOf2 = int(dataOf2)
                dataOf3 = int(dataOf3)
                result = dataOf2*dataOf3
            except:
                errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        self.frame.setVariable(self.instruction["arg1Val"], typeOf2, result)
        return
    def __IDIV(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        if (typeOf2 == 'int' and typeOf3 == 'int'):
            try:
                dataOf2 = int(dataOf2)
                dataOf3 = int(dataOf3)
            except:
                errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
            if (dataOf3 == 0):
                    errorHandling(ErrorTypes.ERR_WRONG_OP_VAL)
            result = dataOf2 // dataOf3
            self.frame.setVariable(self.instruction["arg1Val"], typeOf2, result)
        else:
            errorHandling(ErrorTypes.ERR_WRONG_OP_VAL)
        return
    def __LT(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == typeOf3):
            if not (dataOf2 == 'nil'):
                self.frame.setVariable(self.instruction["arg1Val"], typeOf2, 'true' if dataOf2 < dataOf3 else 'false')
                return
        
        errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        
        
        return
    def __GT(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == typeOf3):
            if not (dataOf2 == 'nil'):
                self.frame.setVariable(self.instruction["arg1Val"], typeOf2, 'true' if dataOf2 > dataOf3 else 'false')
                return
        
        errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __EQ(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)

        if (typeOf2 == typeOf3 or typeOf2 == 'nil' or typeOf3 == 'nil'):
                self.frame.setVariable(self.instruction["arg1Val"], typeOf2, 'true' if dataOf2 == dataOf3 else 'false')
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __AND(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == 'bool' and typeOf3 == 'bool'):
            self.frame.setVariable(self.instruction["arg1Val"], typeOf2, dataOf2 and dataOf3)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __OR(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == 'bool' and typeOf3 == 'bool'):
            self.frame.setVariable(self.instruction["arg1Val"], typeOf2, dataOf2 or dataOf3)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __STRI2INT(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if ((typeOf2 == 'string' and typeOf3 == 'int')):
            try:
                self.frame.setVariable(self.instruction["arg1Val"], typeOf2, ord(dataOf2[dataOf3]))
            except:
                errorHandling(ErrorTypes.ERR_STRING)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __CONCAT(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (dataOf2 == None):
            dataOf2 = ''
        if (dataOf3 == None):
            dataOf3 == ''
        
        if (typeOf2 == 'string' and typeOf3 == 'string'):
            self.frame.setVariable(self.instruction["arg1Val"], typeOf2, str(dataOf2) + str(dataOf3))
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __GETCHAR(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == 'string' and typeOf3 == 'int'):
            try:
                self.frame.setVariable(self.instruction["arg1Val"], typeOf2, dataOf2[dataOf3])
            except:
                errorHandling(ErrorTypes.ERR_STRING)
        return
    def __SETCHAR(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == 'int' and typeOf3 == 'string'):
            variable1 = self.frame.getVariable(self.instruction["arg1Val"])
            try:
                variableNew = variable1["data"][:int(dataOf2)] + dataOf3[0] + variable1["data"][int(dataOf2) + 1:]
            except:
                errorHandling(ErrorTypes.ERR_STRING)
            self.frame.setVariable(self.instruction["arg1Val"], self.instruction["arg1"], variableNew)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    
    # label symb symb 
    def __JUMPIFEQ(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == typeOf3 or typeOf2 == 'nil' or typeOf3 == 'nil'):
            if (dataOf2 == dataOf3):
                self.labels.jumpToLabel(self.instruction["arg1Val"], self.instrCounter)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return
    def __JUMPIFNEQ(self):
        dataOf2, typeOf2 = self.returnDataType(2)
        dataOf3, typeOf3 = self.returnDataType(3)
        
        if (typeOf2 == typeOf3 or typeOf2 == 'nil' or typeOf3 == 'nil'):
            if (dataOf2 != dataOf3):
                self.labels.jumpToLabel(self.instruction["arg1Val"], self.instrCounter)
        else:
            errorHandling(ErrorTypes.ERR_OPERAND_TYPE)
        return

####################################################################
def getOrder(getSorted):
    return getSorted.get('order')

def sortOrder(getSorted):
    getSorted.dictionary.sort(key=getOrder)
    array = []
    for instruction in getSorted.dictionary:
        if (instruction["order"] in array):
            errorHandling(ErrorTypes.ERR_XML_STRUCTURE)
        array.append(instruction["order"])

parsed = ParseArguments()

parsed.main()

checkedXML = ParseXML(parsed.tree, parsed.inputFile)

checkedXML.main()

sortOrder(checkedXML)

checkedParams = ParseInstructions(checkedXML.dictionary, checkedXML.instructionNum, checkedXML.inputFile)
checkedParams.main()
exit(0)