import xml.etree.ElementTree as ET
import sys, getopt
import re

correct_instructions = {"RETURN" : 0, "BREAK" : 0, "CREATEFRAME" : 0, "PUSHFRAME" : 0, "POPFRAME" : 0,
                        "CALL" : 1, "LABEL" : 1, "JUMP" : 1, "PUSHS" : 1, "WRITE" : 1, "EXIT" : 1,
                        "DPRINT" : 1, "DEFVAR" : 1, "POPS" : 1, "MOVE" : 2, "INT2CHAR" : 1, "TYPE" : 2,
                        "STRLEN" : 2, "NOT" : 2, "READ": 2, "ADD" : 3, "SUB" : 3, "MUL" : 3, "IDIV" : 3,
                        "LT" : 3, "GT" : 3, "EQ" : 3, "AND" : 3, "OR" : 3, "STRI2INT" : 3, "CONCAT" : 3,
                        "GETCHAR" : 3, "SETCHAR" : 3, "JUMPIFEQ" : 3, "JUMPIFNEQ" : 3}

class Instruction:

    def __init__(self, name : str, argument : list, order):
        self.name = name.upper()
        self.arguments = argument
        self.order = int(order)

    # for better debug
    def __str__(self):
        return str(self.order) + ". " + self.name + " " + " ".join(str(i) for i in self.arguments)

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

def help():
    print("Usage: \tpython3 iterpret.py [--help] [--source=file , --input=file]")
    print("--help:\t Prints help. Cannot be used with other options.")
    print("--input=file: \tInput file with XML representation of source code. If not set, input is read from STDIN.")
    print("--source=file: \tFile with input used for interpretation of the code. If not set, intput read from STDIN")
    print("Atleast one of --source or --input needs to be set.")

# function to check all arguments
def check_args():
    input_f = None
    source_f = None

    if (len(sys.argv) > 3):
        help()
        exit(10)
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "", ["help", "input=", "source="])
    except:
        help()
        sys.exit(10)

    for opt, arg in options:
        if opt == '--help' and len(options) == 1:
            help()
            exit(0)
        elif opt == '--help' and len(options) != 1:
            help()
            sys.stderr.write("--help cant be used with any other argument\n")
            exit(10)
        if opt == "--source":
            source_f = arg
        elif opt == "--input":
            input_f = arg

    if not input_f and not source_f:
        sys.stderr.write("Atleast one of --source or --input needs to be set\n")
        exit(10)
    return input_f, source_f

# MBY DONT NEED THIS FUNC
# read lines from file or from stdin 
def read_lines(file):
    data = None
    if input_f != None:
        try:
            f = open(file,"r")
            data = f.readlines()
        except:
            sys.stderr.write(f"Could open file {file}\n")
            exit(11)
    else:
        data = sys.stdin.readlines()
    # remove endlines
    data = [l.strip() for l in data]
    return data

def check_xml_elements(root, correct_instructions):
     # CHECK if root has program attrib
    if (root.tag != "program"):
        sys.stderr.write("Wrong root tag.\n")
        exit(32)

    # loop through instructions
    for child in root:
        instr = child.get("opcode")
        # check if only instructions are present
        if (instr not in correct_instructions):
            sys.stderr.write("Wrong instruction name\n")
            exit(32)

        # check if only instruction tag is used
        if ( child.tag != "instruction" ):
            sys.stderr.write("Wrong element tag, it should be instruction\n")
            exit(32)

        for attribute in child.attrib:
            if ( attribute not in ('opcode','order') ):
                sys.stderr.write("Wrong element attribute was used, should be 'order' or 'opcode'\n")
                exit(32)

        # loop through instruction arguments
        arg_cnt = 0 # number of instructions in an instruction
        arg_n = 0 # argument number
        for args in child:
            arg_cnt += 1
            if ( args.tag not in ('arg1','arg2','arg3') ):
                sys.stderr.write("Invalid arg tag number was used.\n")
                exit(32)
            arg_n = re.search(r"\d+(\.\d+)?", args.tag)
            if arg_n == None:
                exit(32)
            arg_n = int(arg_n.group(0))

        # check instruction has correct number of arguments
        if (arg_cnt != correct_instructions.get(instr)):
            sys.stderr.write(f"Incorrect argument count for instruction {instr}\n")
            exit(32)
        # check if argument number is the same as the amount of arguments
        elif (arg_n != arg_cnt):
            sys.stderr.write(f"Instruction {instr} has arg{arg_n} but has only {arg_cnt} arguments\n")
            exit(32)
    return


# function to read instruction from given xml file
def read_instructions(root) -> list:
    instructions_l = []
    for child in root:
        arguments_l = []
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

        instr = Instruction(child.get("opcode"),arguments_l, child.get("order"))
        instructions_l.append(instr)

    # sort instruction through their opcode
    instructions_l.sort(key=lambda instr : instr.order)
    if (instructions_l == None):
        exit(32)

    return instructions_l


# debug function
def print_instructions(instructions_l : list):
    for inst in instructions_l:
        print(inst)
    return

# replace all escape sequencies
def replace_escape(instructions_l) -> list:
    for instruction in instructions_l:
        for argument in instruction.arguments:
            if ( argument.typ == "string" ):
                to_replace = re.findall(r'\\[0-9][0-9][0-9]',argument.value)
                for value in to_replace:
                    new_value = chr(int(value[1::1]))
                    argument.value = argument.value.replace(value, new_value)

    return instructions_l

# find labels
def find_labels(instructions_l) -> dict:
    labels = {}
    return labels

###############################################
## MAIN CODE
input_f, source_f = check_args()
input_data = read_lines(input_f)

try:
    root = ET.fromstringlist(input_data)
except:
    sys.stderr.write("XML file wasnt well-formated.\n")
    exit(31)

check_xml_elements(root, correct_instructions)

instructions = read_instructions(root)

replace_escape(instructions)

print_instructions(instructions)
