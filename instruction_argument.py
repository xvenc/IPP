correct_instructions = {"RETURN" : 0, "BREAK" : 0, "CREATEFRAME" : 0, "PUSHFRAME" : 0, "POPFRAME" : 0,
                        "CALL" : 1, "LABEL" : 1, "JUMP" : 1, "PUSHS" : 1, "WRITE" : 1, "EXIT" : 1,
                        "DPRINT" : 1, "DEFVAR" : 1, "POPS" : 1, "MOVE" : 2, "INT2CHAR" : 1, "TYPE" : 2,
                        "STRLEN" : 2, "NOT" : 2, "READ": 2, "ADD" : 3, "SUB" : 3, "MUL" : 3, "IDIV" : 3,
                        "LT" : 3, "GT" : 3, "EQ" : 3, "AND" : 3, "OR" : 3, "STRI2INT" : 3, "CONCAT" : 3,
                        "GETCHAR" : 3, "SETCHAR" : 3, "JUMPIFEQ" : 3, "JUMPIFNEQ" : 3}

class Instruction:

    def __init__(self, opcode : str, argument : list, order):
        self.opcode = opcode
        self.arguments = argument
        self.order = int(order)

    # for better debug
    def __str__(self):
        return str(self.order) + ". " + self.opcode + " " + " ".join(str(i) for i in self.arguments)

# TODO add check for argument types and values
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

    def check_value(self):
        pass

class Frames:

    def __init__(self):
        self.GF = {}
        self.LF = []
        self.TF = None
