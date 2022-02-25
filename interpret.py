import xml.etree.ElementTree as ET
import sys, getopt
import re
from instruction_argument import *

# TODO class frame to store variables

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

# check if xml input file has correct format
def check_xml_elements(root, correct_instructions):
     # CHECK if root has program attrib
    if (root.tag != "program"):
        sys.stderr.write("Wrong root tag.\n")
        exit(32)

    # loop through instructions
    for child in root:
        instr = child.get("opcode").upper()
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
    position = 0
    used_labels = []
    for instr in instructions_l:
        if instr.opcode == "LABEL":
            label_name = str(instr.arguments[0])
            if label_name not in used_labels:
                labels[label_name] = position
                used_labels.append(label_name)
            else:
                sys.stderr.write(f'Label name {label_name} was already used\n')
                exit(52)
        position += 1
    return labels


# read from frame
def read_from_frame(arg, frames):
    data = None
    if arg.typ == "var":
        frame = arg.value.split("@",1)[0]
        var_name = arg.value.split("@",1)[1]
        if frame == 'GF':
            if var_name in frames.GF:
                data = frames.GF[var_name]
            else:
                sys.stderr.write(f"Var {var_name} not in GF\n")
                exit(54)
        elif frame == 'TF':
            if (frames.TF != None):
                if var_name in frames.TF:
                    data = frames.TF[var_name]
                else:
                    sys.stderr.write(f"Var {var_name} not in TF\n")
                    exit(54)
            else:
                sys.stderr.write(f"LF doesnt exist\n")
                exit(55)

        elif frame == "LF":
            if (len(frames.LF) != 0):
                if var_name in frames.LF[-1]:
                    data = frames.LF[-1][var_name]
                else:
                    sys.stderr.write(f"Var {var_name} not in LF\n")
                    exit(54)
            else:
                    sys.stderr.write(f"LF doesnt exist\n")
                    exit(55)
        else:
            sys.stderr.write(f"Given frame '{frame}' dont exist\n")
            sys.exit(55)

    elif arg.typ == 'string':
        data = str(arg.value)
    elif arg.typ == 'int':
        data = int(arg.value)
    elif arg.typ == 'bool':
        data = arg.value == "true"
    elif arg.typ == 'nil':
        data = 'nil'

    return data

# function to write data to frame
def write_to_frame(data_to_write, argument, frames):

    if argument.typ == 'var':
        frame = argument.value.split("@",1)[0]
        var_name = argument.value.split("@",1)[1]
        if frame == 'GF':
            frames.GF[var_name] = data_to_write
        elif frame == 'TF':
            if (frames.TF != None):
                frames.TF[var_name] = data_to_write
        elif frame == "LF":
            frames.LF[-1][var_name] = data_to_write
        else:
            sys.stderr.write(f"Given frame '{frame}' dont exist\n")
            sys.exit(55)

# function to get index of label to which will be jumped
def get_label_index(argument, labels) -> int:
    index = 0
    label_name = argument.value
    if (label_name in labels):
        index = labels[label_name]
    else:
        sys.stderr.write(f"Label {label_name} doesnt exist\n")
        exit(55)
    return index

def print_frame(frame, info : str):
    print('\n',info)
    for var in frame:
        print(f'INFO: Variable: {var} contains: {frame[var]}')

# TODO interpret
def interpret(instructions_l, labels):
    # GF = {}
    # LF = []
    # TF = None 
    frames = Frames() # all frames
    index = 0 # index of currently processed instruction
    instruction = None # currently processed instruction
    # frame = None # name of frame with which the instruction works
    # var_name = None # variable name from on of the frames
    data_to_write = None # data to write to the frame
    data_from_frame = None # data read from the frame
    label_name = None # name of the label to jump to
    executed_instructions = 0
    while index < len(instructions_l):
        instruction = instructions_l[index]
        index += 1
        executed_instructions += 1
        if instruction.opcode == 'MOVE':

            data_to_write = read_from_frame(instruction.arguments[1], frames)
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'CREATEFRAME':

            frames.create_tf()

        elif instruction.opcode == 'PUSHFRAME':
            # TODO PUSHFRAME
            pass
        elif instruction.opcode == 'POPFRAME':
            # TODO POPFRAME
            pass
        elif instruction.opcode == 'DEFVAR':

            data_to_write = None
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'CALL':
            # TODO CALL
            pass
        elif instruction.opcode == 'RETURN':
            # TODO RETURN
            pass
        elif instruction.opcode == 'PUSHS':
            # TODO PUSHS
            pass
        elif instruction.opcode == 'POPS':
            # TODO POPS
            pass
        elif instruction.opcode == 'ADD':
            # TODO ADD
            pass
        elif instruction.opcode == 'SUB':
            # TODO SUB
            pass
        elif instruction.opcode == 'IDIV':
            # TODO IDIV
            pass
        elif instruction.opcode == 'MUL':
            # TODO MUL
            pass
        elif instruction.opcode == 'LT':
            # TODO LT
            pass
        elif instruction.opcode == 'GT':
            # TODO GT
            pass
        elif instruction.opcode == 'EQ':
            # TODO EQ
            pass
        elif instruction.opcode == 'AND':
            # TODO AND
            pass
        elif instruction.opcode == 'OR':
            # TODO OR
            pass
        elif instruction.opcode == 'NOT':
            # TODO NOT
            pass
        elif instruction.opcode == 'INT2CHAR':
            # TODO INT2CHAR
            pass
        elif instruction.opcode == 'STRI2INT':
            # TODO STRI2INT
            pass
        elif instruction.opcode == 'READ':
            # TODO READ
            pass
        elif instruction.opcode == 'WRITE':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            print(data_from_frame, end="")

        elif instruction.opcode == 'CONCAT':
            # TODO CONCAT
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)
            if type(data_first) == str and type(data_second) == str:
                data_to_write = str(data_first) + str(data_second)
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'STRLEN':
            # TODO STRLEN
            pass
        elif instruction.opcode == 'GETCHAR':
            # TODO GETCHAR
            pass
        elif instruction.opcode == 'SETCHAR':
            # TODO SETCHAR
            pass
        elif instruction.opcode == 'TYPE':
            # TODO TYPE
            pass
        elif instruction.opcode == 'LABEL':
            # TODO LABEL
            pass
        elif instruction.opcode == 'JUMP':

            index = get_label_index(instruction.arguments[0],labels)

        elif instruction.opcode == 'JUMPIFEQ':
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) == type(data_second) and data_first == data_second:
                index = get_label_index(instruction.arguments[0], labels)

        elif instruction.opcode == 'JUMPIFNEQ':
            # TODO JUMPIFNEQ
            pass
        elif instruction.opcode == 'EXIT':
            # TODO EXIT
            pass
        elif instruction.opcode == 'DPRINT':
            # TODO DPRINT
            pass
        elif instruction.opcode == 'BREAK':
            # TODO BREAK
            sys.stderr.write(f"Index of current instruction: {index}\n")
            sys.stderr.write(f"Number of executed instructions: {executed_instructions}\n")
            sys.stderr.write(f"Global frame: {frames.GF}\n")
            sys.stderr.write(f"Local frame: {frames.LF}\n")
            sys.stderr.write(f"Temporary frame: {frames.TF}\n")
    # debug
    #print_frame(frames.GF, "GF:")
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
labels = find_labels(instructions)
interpret(instructions, labels)
# print_instructions(instructions)
