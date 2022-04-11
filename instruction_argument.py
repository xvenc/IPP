import xml.etree.ElementTree as ET
import sys, re
# dictionary with all acceptable instructions and with number of their arguments
correct_instructions = {"RETURN" : 0, "BREAK" : 0, "CREATEFRAME" : 0, "PUSHFRAME" : 0, "POPFRAME" : 0,
                        "CALL" : 1, "LABEL" : 1, "JUMP" : 1, "PUSHS" : 1, "WRITE" : 1, "EXIT" : 1,
                        "DPRINT" : 1, "DEFVAR" : 1, "POPS" : 1, "MOVE" : 2, "INT2CHAR" : 2, "TYPE" : 2,
                        "STRLEN" : 2, "NOT" : 2, "READ": 2, "ADD" : 3, "SUB" : 3, "MUL" : 3, "IDIV" : 3,
                        "LT" : 3, "GT" : 3, "EQ" : 3, "AND" : 3, "OR" : 3, "STRI2INT" : 3, "CONCAT" : 3,
                        "GETCHAR" : 3, "SETCHAR" : 3, "JUMPIFEQ" : 3, "JUMPIFNEQ" : 3}

# dictionary with instructions and lists with their argument types
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

# Function to exit and print message to stderr
def my_exit(message : str, exit_code : int):
    sys.stderr.write(message)
    sys.exit(exit_code)

# class to represent instructions 
class Instruction:

    def __init__(self, opcode : str, argument : list, order):
        self.opcode = opcode
        self.arguments = argument
        self.order = int(order)

    # for better debug
    def __str__(self):
        return self.opcode

    # check if instruction have correct number and type of arguments
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

# class to represent instruction arguments 
class Argument:

    def __init__(self, typ, value, order : int):
        self.typ = typ
        if (value != None):
            self.value = value
        else:
            self.value = ""
        # replace all escape sequences in string
        if typ == "string":
            to_replace = re.findall(r'\\[0-9][0-9][0-9]',self.value)
            for old_value in to_replace:
                new_value = chr(int(old_value[1::1]))
                self.value = self.value.replace(old_value, new_value)
        self.order = int(order)

    # for better debug
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.typ

    # help function used when checking if instruction have correct arguments types
    def assign_type(self, expected):
        if self.typ == "label":
            return "label"
        elif self.typ in ("int", "string", "bool", "nil", "var") and expected == "symb":
            return "symb"
        elif self.typ == "var" and expected == "var":
            return "var"
        elif self.typ == "type":
            return "type"

# class to represent and to keep all the frames together
class Frames:

    def __init__(self):
        self.GF = {}
        self.LF = []
        self.TF = None

    # create temporary frame
    def create_tf(self):
        self.TF = dict()

    # function to get data from frame specified in argument
    def get_data(self, arg):
        frame = arg.value.split("@",1)[0]
        variable = arg.value.split("@",1)[1]
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

    # function to write data to frame specified in frame
    def write_data(self, frame, variable, data_to_write):
        if frame == 'GF':
            self.GF[variable] = data_to_write
        elif frame == 'TF':
            if (self.TF != None):
                self.TF[variable] = data_to_write
            else:
                return 55
        elif frame == "LF":
            if len(self.LF) != 0:
                self.LF[-1][variable] = data_to_write
            else:
                return 55
        else:
            return 55
        return 0

# class to represent nil type
class NIL:

    def __init__(self):
        pass

    def __str__(self):
        return ""

    def __repr__(self):
        return "nil"

# class to check if xml input file was correctly formated
class XML_checker:

    def __init__(self,source_data):
        try:
            self.root = ET.fromstringlist(source_data)
        except:
            my_exit("XML file wasnt well-formated\n", 31)

    # check if xml input file has correct format
    def check_xml_elements(self):
        # check if root has program attrib
        if (self.root.tag != "program"):
            my_exit("Wrong root tag\n", 32)

    # check root attributes 
        for prog_attrib in self.root.attrib:
            if ( prog_attrib not in ('name','language','description') ):
                my_exit("Wrong element attribute was used, should be 'order' and 'opcode'\n", 32)

        if (self.root.get("language") != "IPPcode22"):
            my_exit("Wrong language\n", 32)

        # loop through instructions
        for child in self.root:
            # check if only attributes opcode and order are used
            for attribute in child.attrib:
                if ( attribute not in ('opcode','order') ):
                    my_exit("Wrong instruction element attribute was used, should be 'order' and 'opcode'\n", 32)
            try:
                instr = child.get("opcode").upper()
                order = int(child.get("order"))
            except:
                my_exit("Opcode or order is not used\n", 32)
            # check if only correct instructions are present
            if (instr not in correct_instructions):
                my_exit("Wrong instruction name\n", 32)

            # check if only instruction tag is used
            if ( child.tag != "instruction" ):
                my_exit("Wrong element tag, it should be instruction\n", 32)

            # loop through instruction arguments
            arg_cnt = 0 # number of instructions in an instruction
            for args in child:
                arg_cnt += 1
                if ( args.tag not in ('arg1','arg2','arg3') ):
                    my_exit("Invalid argument tag number was used\n", 32)

            if (arg_cnt != correct_instructions.get(instr)):
                my_exit(f"Incorrect argument count for instruction {instr}\n", 32)

        return

    # function to read instruction from given xml file and return them in a list
    def read_instructions(self) -> list:
        instructions_l = [] # list of all instructions
        for child in self.root:
            arguments_l = [] # list for arguments
            for args in child:
                # get argument number
                arg_n = re.search(r"\d+(\.\d+)?", args.tag)
                if arg_n == None:
                    exit(32)
                arg_n = arg_n.group(0)

                argument = Argument(args.get("type"), args.text, int(arg_n))
                arguments_l.append(argument)

            # sort arguments
            arguments_l.sort(key= lambda argument : argument.order)

            # check if arguments go one after other
            index = 1
            for arg in arguments_l:
                if arg.order != index:
                    my_exit(f"Instruction {child} has wrong arguments\n", 32)
                index += 1

            instr = Instruction(child.get("opcode").upper(),arguments_l, child.get("order"))
            instructions_l.append(instr)

        # sort instruction through their opcode
        instructions_l.sort(key=lambda instr : instr.order)
        if (instructions_l == None):
            exit(32)
        # check if instructions are ordered from 1 to n
        # and if there are no duplicit values
        prev_order = 0
        for instr in instructions_l:
            if instr.order <= prev_order:
                my_exit(f"Instruction {instr} has wrong order\n", 32)
            prev_order = instr.order


        return instructions_l
