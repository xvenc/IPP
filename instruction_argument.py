import re
from traceback import print_tb


correct_instructions = {"RETURN" : 0, "BREAK" : 0, "CREATEFRAME" : 0, "PUSHFRAME" : 0, "POPFRAME" : 0,
                        "CALL" : 1, "LABEL" : 1, "JUMP" : 1, "PUSHS" : 1, "WRITE" : 1, "EXIT" : 1,
                        "DPRINT" : 1, "DEFVAR" : 1, "POPS" : 1, "MOVE" : 2, "INT2CHAR" : 2, "TYPE" : 2,
                        "STRLEN" : 2, "NOT" : 2, "READ": 2, "ADD" : 3, "SUB" : 3, "MUL" : 3, "IDIV" : 3,
                        "LT" : 3, "GT" : 3, "EQ" : 3, "AND" : 3, "OR" : 3, "STRI2INT" : 3, "CONCAT" : 3,
                        "GETCHAR" : 3, "SETCHAR" : 3, "JUMPIFEQ" : 3, "JUMPIFNEQ" : 3}

correct_instruction_types = {"RETURN" : None, "BREAK" : None, "CREATEFRAME" : None, 
                        "PUSHFRAME" : None, "POPFRAME" : None, "CALL" : ["label"], 
                        "LABEL" : ["label"], "JUMP" : ["label"], "PUSHS" : ["symb"], 
                        "WRITE" : ["symb"], "EXIT" : ["symb"], "DPRINT" : ["symb"],
                        "DEFVAR" : ["var"], "POPS" : ["var"], "MOVE" : ["var", "symb"],
                        "INT2CHAR" : ["var","symb"], "TYPE" : ["var", "symb"], 
                        "STRLEN" : ["var", "symb"], "NOT" : ["var", "symb"], 
                        "READ": ["var", "type"], "ADD" : ["var", "symb", "symb"], 
                        "SUB" : ["var", "symb", "symb"], "MUL" : ["var", "symb", "symb"],
                        "IDIV" : ["var", "symb", "symb"], "LT" : ["var", "symb", "symb"], 
                        "GT" : ["var", "symb", "symb"], "EQ" : ["var", "symb", "symb"], 
                        "AND" : ["var", "symb", "symb"],  "OR" : ["var", "symb", "symb"], 
                        "STRI2INT" : ["var", "symb", "symb"], "CONCAT" : ["var", "symb", "symb"], 
                        "GETCHAR" : ["var", "symb", "symb"], "SETCHAR" : ["var", "symb", "symb"],
                        "JUMPIFEQ" : ["label", "symb", "symb"], "JUMPIFNEQ" : ["label", "symb", "symb"]}


class Instruction:

    def __init__(self, opcode : str, argument : list, order):
        self.opcode = opcode
        self.arguments = argument
        self.order = int(order)

    # for better debug
    def __str__(self):
        return self.opcode
        #+ " " + " ".join(str(i) for i in self.arguments)
    
    def check_instruction(self):
        postion = 0
        if self.opcode in correct_instruction_types:
            if len(self.arguments) == 0 and not correct_instruction_types[self.opcode]:
                return True
            for expected in correct_instruction_types[self.opcode]:
                if expected == self.arguments[postion].assign_type(expected):
                    postion += 1
                else:
                    return False
        else: 
            return False
        return True        
        

class Argument:

    def __init__(self, typ, value, order : int):
        self.typ = typ
        if (value != None):
            self.value = value
        else:
            self.value = ""
        self.order = int(order)

    # for better debug
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.typ
    # add arg other and check if it should be symb so check if in symb 
    def assign_type(self, expected):
        if self.typ == "label":
            return "label"
        elif self.typ in ("int", "string", "bool", "nil", "var") and expected == "symb":
            return "symb"
        elif self.typ == "var" and expected == "var":
            return "var"
        elif self.typ == "type":
            return "type"


class Frames:

    def __init__(self):
        self.GF = {}
        self.LF = []
        self.TF = None

    def create_tf(self):
        self.TF = dict()

    def read_data(self, variable, frame):
        if frame == 'GF':
            if variable in self.GF:
                return self.GF[variable], 0
            else:
                return None, 54
        elif frame == 'TF':
            if (self.TF != None):
                if variable in self.TF:
                    return self.TF[variable], 0
                else:
                    return None, 54
            else:
                return None, 55
        elif frame == "LF":
            if (len(self.LF) != 0):
                if variable in self.LF[-1]:
                    return self.LF[-1][variable], 0
                else:
                    return None, 54
            else:
                return None, 55
        else:
            return None, 55

    def write_data(self, frame, variable, data_to_write):
        if frame == 'GF':
            self.GF[variable] = data_to_write
        elif frame == 'TF':
            if (self.TF != None):
                self.TF[variable] = data_to_write
            else:
                return 55
        elif frame == "LF":
            if len(self.TF) != 0:
                self.LF[-1][variable] = data_to_write
            else:
                return 55
        else:
            return 55
        return 0

class NIL:

    def __init__(self):
        pass

    def __str__(self):
        return ""
    
    def __repr__(self):
        return "nil"