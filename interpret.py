import xml.etree.ElementTree as ET
import sys, getopt
import re
from instruction_argument import *

def help():
    print("Usage: \tpython3 iterpret.py [--help] [--source=file , --input=file]")
    print("--help:\t Prints help. Cannot be used with other options.")
    print("--input=file: \tInput file with XML representation of source code. If not set, input is read from STDIN.")
    print("--source=file: \tFile with input used for interpretation of the code. If not set, intput read from STDIN")
    print("Atleast one of --source or --input needs to be set.")

def my_exit(message : str, exit_code : int):
    sys.stderr.write(message)
    sys.exit(exit_code)

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
            my_exit("--help cant be used with any other argument\n",10)
        if opt == "--source":
            source_f = arg
        elif opt == "--input":
            input_f = arg

    if not input_f and not source_f:
        my_exit("Atleast one of --source or --input needs to be set\n", 10)
    return input_f, source_f

# read lines from file or from stdin 
def read_lines(file):
    data = None
    if input_f != None:
        try:
            f = open(file,"r")
            data = f.readlines()
        except:
            my_exit(f"Could open file {file}\n", 11)
    else:
        data = sys.stdin.readlines()
    # remove endlines
    data = [l.strip() for l in data]
    return data

# check if xml input file has correct format
def check_xml_elements(root, correct_instructions):
     # check if root has program attrib
    if (root.tag != "program"):
        my_exit("Wrong root tag\n", 32)

   # check root attributes 
    for prog_attrib in root.attrib:
        if ( prog_attrib not in ('name','language','description') ):
            my_exit("Wrong element attribute was used, should be 'order' and 'opcode'\n", 32)

    if (root.get("language") != "IPPcode22"):
        my_exit("Wrong language\n", 32)

    # loop through instructions
    for child in root:
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


# function to read instruction from given xml file
def read_instructions(root) -> list:
    instructions_l = [] # list of all instructions
    for child in root:
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

        instr = Instruction(child.get("opcode"),arguments_l, child.get("order"))
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

def check_argument_types(instructions_l):
    # check if instruction has correct argument types
    for instr in instructions_l:
        check = instr.check_instruction()
        if check == False:
            my_exit(f"Wrong argument types for instruction {instr}\n", 32)


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

# find labels all labels and check if there is no redefinition of a label
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
                my_exit(f"Label name {label_name} was already used\n", 52)
        position += 1
    return labels

# function to get index of label to which will be jumped
def get_label_index(argument, labels) -> int:
    index = 0
    label_name = argument.value
    if (label_name in labels):
        index = labels[label_name]
    else:
        my_exit(f"Label '{label_name}' doesnt exist\n", 52)
    return index


nil = NIL()
# read data from frame or directli from instruction if it's constant
def read_from_frame(arg, frames):
    data = None
    if arg.typ == "var":
        frame = arg.value.split("@",1)[0]
        var_name = arg.value.split("@",1)[1]
        data, code = frames.read_data(var_name, frame)
        if code == 55:
            my_exit("Frame doesnt exist\n", code)
        elif code == 54:
            my_exit(f"Variable '{var_name}' doesnt exist\n", code)
    elif arg.typ == 'string':
        data = str(arg.value)
    elif arg.typ == 'int':
        try:
            data = int(arg.value)
        except:
            my_exit("Data can be only integer\n", 57)
    elif arg.typ == 'bool':
        if arg.value == "true":
            data = True
        else:
            data = False
    elif arg.typ == 'nil':
        if arg.value == 'nil':
            data = nil
        else:
            my_exit("Nil type can only have nil value\n", 52)
    elif arg.typ == 'type':
        data = str(arg.value)

    return data

# function to write data to frame
def write_to_frame(data_to_write, argument, frames):

    if argument.typ == 'var':
        frame = argument.value.split("@",1)[0]
        var_name = argument.value.split("@",1)[1]
        code = frames.write_data(frame, var_name, data_to_write)
        if code != 0:
            my_exit(f"Given frame '{frame}' doesnt exist\n", code)

def interpret(instructions_l, labels):

    frames = Frames() # all frames
    index = 0 # index of currently processed instruction
    instruction = None # currently processed instruction
    data_to_write = None # data to write to the frame
    data_from_frame = None # data read from the frame
    executed_instructions = 0
    nil_type = NIL()

    while index < len(instructions_l):
        instruction = instructions_l[index]
        index += 1
        executed_instructions += 1

        if instruction.opcode == 'MOVE':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
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

            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_first + data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'SUB':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_first - data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'IDIV':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != int or type(data_second) != int:

                my_exit("Wrong operand types\n", 53)
            if data_second == 0:
                my_exit("Zero division error\n", 57)

            data_to_write = data_first // data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)
        elif instruction.opcode == 'MUL':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_first * data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)


        elif instruction.opcode == 'LT':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) == type(data_second):
                data_to_write = data_first < data_second
            elif type(data_first) == nil_type or type(data_second) == nil_type:
                my_exit("Wrong operand types\n", 53)
            else:
                my_exit("Wrong operand types\n", 53)

            write_to_frame(data_to_write, instruction.arguments[0], frames)


        elif instruction.opcode == 'GT':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) == type(data_second):
                data_to_write = data_first > data_second
            elif type(data_first) == nil_type or type(data_second) == nil_type:
                my_exit("Wrong operand types\n", 53)
            else:
                my_exit("Wrong operand types\n", 53)

            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'EQ':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)


            if type(data_first) == type(data_second) or type(data_first) == nil_type or type(data_second) == nil_type:
                data_to_write = data_first == data_second
            else:
                my_exit("Wrong operand types\n", 53)

            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'AND':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != bool or type(data_second) != bool:
                my_exit("Wrong operand types\n", 53)
            
            data_to_write = data_first and data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'OR':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != bool or type(data_second) != bool:
                my_exit("Wrong operand types\n", 53)
            
            data_to_write = data_first or data_second
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'NOT':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)

            if type(data_first) == bool:
                data_to_write = not data_first
            else:
                my_exit("Wrong operand types\n", 53)
            
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'INT2CHAR':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)

            if type(data_first) != int:
                my_exit("Wrong operand types\n", 53)
            try:
                data_to_write = chr(data_first)
            except ValueError:
                my_exit("Wrong integer number in instruction INT2CHAR\n", 58)
            
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'STRI2INT':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != str or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)
            
            if data_second < 0 or data_second >= len(data_first):
                my_exit("Index out of boundaries of the string\n", 58)
            
            data_to_write = ord(data_first[data_second])

        elif instruction.opcode == 'READ':
            # TODO READ
            pass
        elif instruction.opcode == 'WRITE':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            print(data_from_frame, end="")

        elif instruction.opcode == 'CONCAT':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != str or type(data_second) != str:
                my_exit("Wrong operand types\n", 53)

            data_to_write = str(data_first) + str(data_second)
            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'STRLEN':

            data_from_frame = read_from_frame(instruction.arguments[0], frames)
            data_second = read_from_frame(instruction.arguments[1], frames)
            if ( type(data_second) != str ):
                my_exit("Wrong operand types\n", 53)

            data_to_write = len(data_second)
            write_to_frame(data_to_write, instruction.arguments[0], frames) 
        elif instruction.opcode == 'GETCHAR':
            data_from_frame = read_from_frame(instruction.arguments[0], frames)

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)
            if type(data_first) != str or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)
            
            if data_second < 0 or data_second >= len(data_first):
                my_exit(f"Index {data_second} out of boundaries of the string\n", 58)

            data_to_write = data_first[data_second]

            write_to_frame(data_to_write, instruction.arguments[0], frames)

        elif instruction.opcode == 'SETCHAR':

            data_to_write = read_from_frame(instruction.arguments[0], frames)
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)
            
            if type(data_first) != int or type(data_second) != str or type(data_to_write) != str:
                my_exit("Wrong operand types\n", 53)

            if (data_first < 0 or data_first >= len(data_to_write)):
                my_exit(f"Index {data_first} out of boundaries of the string\n", 58)
            
            data_to_write = list(data_to_write)
            data_to_write[data_first] = data_second[0]
            data_to_write = "".join(data_to_write)

            write_to_frame(data_to_write, instruction.arguments[0], frames)
            
        elif instruction.opcode == 'TYPE':
            # TODO TYPE
            pass
        elif instruction.opcode == 'LABEL':

            pass

        elif instruction.opcode == 'JUMP':

            index = get_label_index(instruction.arguments[0],labels)

        elif instruction.opcode == 'JUMPIFEQ':
            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != type(data_second):
                my_exit("Wrong operand types\n", 53)
            if data_first == data_second:
                index = get_label_index(instruction.arguments[0], labels)

        elif instruction.opcode == 'JUMPIFNEQ':

            data_first = read_from_frame(instruction.arguments[1], frames)
            data_second = read_from_frame(instruction.arguments[2], frames)

            if type(data_first) != type(data_second):
                my_exit("Wrong operand types\n", 53)

            if data_first != data_second:
                index = get_label_index(instruction.arguments[0], labels)

        elif instruction.opcode == 'EXIT':

            data_first = read_from_frame(instruction.arguments[0], frames)
            if type(data_first) != int:
                my_exit("Wrong operand types\n", 53)
            if data_first >= 0 and data_first <= 49:
                sys.exit(data_first)
            else:
                my_exit(f"Invalid exit number value '{data_first}'\n", 57)

        elif instruction.opcode == 'DPRINT':

            data_first = read_from_frame(instruction.arguments[0], frames)
            print(data_first,file=sys.stderr,end="")

        elif instruction.opcode == 'BREAK':

            sys.stderr.write(f"Index of current instruction: {index}\n")
            sys.stderr.write(f"Number of executed instructions: {executed_instructions}\n")
            sys.stderr.write(f"Global frame: {frames.GF}\n")
            sys.stderr.write(f"Local frame: {frames.LF}\n")
            sys.stderr.write(f"Temporary frame: {frames.TF}\n")


# debug functions
def print_instructions(instructions_l : list):
    for inst in instructions_l:
        print(inst)
    return

def print_frame(frame, info : str):
    print('\n',info)
    for var in frame:
        print(f'INFO: Variable: {var} contains: {frame[var]}')



###############################################
## MAIN CODE
input_f, source_f = check_args()
input_data = read_lines(source_f)
try:
    root = ET.fromstringlist(input_data)
except:
    my_exit("XML file wasnt well-formated\n", 31)

check_xml_elements(root, correct_instructions)

instructions = read_instructions(root)
check_argument_types(instructions)
replace_escape(instructions)
labels = find_labels(instructions)
interpret(instructions, labels)
# print_instructions(instructions)
