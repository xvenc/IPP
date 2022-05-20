# interpret.py
# Solution for 2. task for IPP 2021/2022
# Author: Václav Korvas VUT FIT 2BIT (xkorva03)
# Main modul to interpret code written in IPPcode22

import sys, getopt, re
from src_interpret.classes import *

# Function to print help if the parametr help is set
def help():
    print("Usage: \tpython3 iterpret.py [--help] [--source=file , --input=file]")
    print("--help:\t Prints help. Cannot be used with other options.")
    print("--input=file: \tInput file with XML representation of source code. If not set, input is read from STDIN.")
    print("--source=file: \tFile with input used for interpretation of the code. If not set, intput read from STDIN")
    print("Atleast one of --source or --input needs to be set.")

# Function to print message to stderr and exits with given return code
def my_exit(message : str, exit_code : int):
    sys.stderr.write(message)
    sys.exit(exit_code)

# function to check all arguments and to check if the combination of arguments was acceptable
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

    for arg in sys.argv[1:]:
        if re.search("^--input=.+$", arg):
            continue
        elif re.search("^--source=.+$", arg):
            continue
        elif arg == "--help":
            continue
        else:
            my_exit("wrong argument", 10)

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
    if file != None:
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

 # check if instruction has correct argument types
def check_argument_types(instructions_l):
    for instr in instructions_l:
        check = instr.check_instruction()
        if check == False:
            my_exit(f"Wrong argument types for instruction {instr}\n", 32)

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

nil = NIL() # special instance of "nil" type used in IPPcode22

# read data from var or symbol if its constant(int,string,bool or nil)
def data_from_const(arg):
    data = None
    if arg.typ == 'string':
        data = str(arg.value)
    elif arg.typ == 'int':
        try:
            data = int(arg.value, 0)
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
    return

# help function used in read instruction to determine type of value
def get_type(data) -> str:
    if data == None:
        return ""
    if type(data) == str:
        return "string"
    if type(data) == int:
        return "int"
    if type(data) == bool:
        return "bool"
    if data == nil:
        return "nil"

# Function to return data read from instruction arguments
# it reads data from frames, or from constants(int,nil, etc.)
def get_data_from_arg(frames, instruction):
    data_first = None
    data_second = None
    data_third = None
    data = None
    for arg in instruction.arguments:
        if (arg.typ == "var" and instruction.opcode not in ("DEFVAR") and arg.order == 1):
            data_first, code = frames.get_data(arg)
            if code == 55:
                my_exit("Frame doesnt exist\n", code)
            elif code == 54:
                my_exit("Variable doesnt exist\n", code)
        if (arg.typ in ("int","string", "bool", "nil") and arg.order == 1):
            data_first = data_from_const(arg)

        if (arg.order in (2,3)):
            if (arg.typ == "var"):
                data, code = frames.get_data(arg)
                if code == 55:
                    my_exit("Frame doesnt exist\n", code)
                elif code == 54:
                    my_exit("Variable doesnt exist\n", code)
            elif arg.typ in ("int","string", "bool", "nil", "type"):
                data = data_from_const(arg)

            if arg.order == 2:
                data_second = data
            elif arg.order == 3:
                data_third = data

    return data_first, data_second, data_third

# main function to interpret given code, it contains one elif statement
# with if for every single instruction, the big if switch runs in while loop
# for all instructions in the instructions list
def interpret(instructions_l, labels, input_f):

    frames = Frames() # all frames
    index = 0 # index of currently processed instruction
    instruction = None # currently processed instruction
    data_to_write = None # data to write to the frame
    executed_instructions = 0 # number of executed instruction used in instruction break
    nil_type = nil # "nil" type to compare with read data if its nil
    data_stack = [] # 'stack' for pushed data
    call_stack = [] # stack of indexes when call and return functions are used
    first_read = True
    # for example AND <var> <symb1> <symb2>
    data_first = None # first data from instruction arguments (<var> from example)
    data_second = None # second data from instruction arguments (<symb1> from example)
    data_third = None # third data from instruction arguments (<symb2> from example)

    # main loop to go through all instructions
    while index < len(instructions_l):
        instruction = instructions_l[index]
        index += 1
        executed_instructions += 1
        write_data = True
        data_first, data_second, data_third = get_data_from_arg(frames, instruction)

        # 'if tree' to determine which instruction should we interpret
        if instruction.opcode == 'MOVE':

            data_to_write = data_second

            if data_to_write == None:
                my_exit("MOVE: Missing value\n", 56)

        elif instruction.opcode == 'CREATEFRAME':

            frames.create_tf()
            write_data = False

        elif instruction.opcode == 'PUSHFRAME':

            if frames.TF == None:
                my_exit("Frame doesnt exist\n",55)

            frames.LF.append(frames.TF)
            frames.TF = None
            write_data = False

        elif instruction.opcode == 'POPFRAME':

            if len(frames.LF) == 0:
                my_exit("No frame is availible\n", 55)

            frames.TF = frames.LF.pop()
            write_data = False

        elif instruction.opcode == 'DEFVAR':

            if instruction.arguments[0].typ == "var":
                data_first, code = frames.get_data(instruction.arguments[0])
                if code == 55:
                    my_exit("Frame doesnt exist\n", code)
                elif code == 0:
                    my_exit("Variable already exists\n", 52)

            data_to_write = None

        elif instruction.opcode == 'CALL':

            call_stack.append(index)
            index = get_label_index(instruction.arguments[0], labels)
            write_data = False

        elif instruction.opcode == 'RETURN':

            if len(call_stack) == 0:
                my_exit("Call stack is empty, there is no index\n", 56)

            index = call_stack.pop()
            write_data = False

        elif instruction.opcode == 'PUSHS':

            if data_first == None:
                my_exit("PUSHS: Missing value\n", 56)
            data_stack.append(data_first)
            write_data = False

        elif instruction.opcode == 'POPS':
            if len(data_stack) == 0:
                my_exit("There is nothing on the stack\n", 56)

            data_to_write = data_stack.pop()

        elif instruction.opcode == 'ADD':

            if data_second == None or data_third == None:
                my_exit("ADD: Missing value\n", 56);
            if type(data_second) != int or type(data_third) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_second + data_third

        elif instruction.opcode == 'SUB':

            if data_third == None or data_second == None:
                my_exit("SUB: Missing value\n", 56);

            if type(data_third) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_second - data_third

        elif instruction.opcode == 'IDIV':

            if data_third == None or data_second == None:
                my_exit("IDIV: Missing value\n", 56);

            if type(data_third) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)
            if data_third == 0:
                my_exit("Zero division error\n", 57)

            data_to_write = data_second // data_third

        elif instruction.opcode == 'MUL':

            if data_third == None or data_second == None:
                my_exit("MUL: Missing value\n", 56);

            if type(data_third) != int or type(data_second) != int:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_third * data_second

        elif instruction.opcode == 'LT':

            if data_third == None or data_second == None:
                my_exit("EQ: Missing value\n", 56);

            if data_third == nil_type or data_second == nil_type:
                my_exit("Wrong operand types\n", 53)

            if type(data_third) != type(data_second):
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_second < data_third

        elif instruction.opcode == 'GT':

            if data_third == None or data_second == None:
                my_exit("GT: Missing value\n", 56);

            if data_third == nil_type or data_second == nil_type:
                my_exit("Wrong operand types\n", 53)

            if type(data_third) != type(data_second):
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_second > data_third

        elif instruction.opcode == 'EQ':

            if data_third == None or data_second == None:
                my_exit("EQ: Missing value\n", 56);

            if type(data_third) == type(data_second) or data_third == nil or data_second == nil:
                data_to_write = data_third == data_second
            else:
                my_exit("Wrong operand types\n", 53)

        elif instruction.opcode == 'AND':

            if data_third == None or data_second == None:
                my_exit("AND: Missing value\n", 56);

            if type(data_third) != bool or type(data_second) != bool:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_third and data_second

        elif instruction.opcode == 'OR':

            if data_third == None or data_second == None:
                my_exit("IDIV: Missing value\n", 56);

            if type(data_third) != bool or type(data_second) != bool:
                my_exit("Wrong operand types\n", 53)

            data_to_write = data_second or data_third

        elif instruction.opcode == 'NOT':

            if data_second == None:
                my_exit("NOT: Missing value\n", 56);

            if type(data_second) == bool:
                data_to_write = not data_second
            else:
                my_exit("Wrong operand types\n", 53)

        elif instruction.opcode == 'INT2CHAR':

            if data_second == None:
                my_exit("INT2CHAR: Missing value\n", 56);
            if type(data_second) != int:
                my_exit("Wrong operand types\n", 53)
            try:
                data_to_write = chr(data_second)
            except ValueError:
                my_exit("Wrong integer number in instruction INT2CHAR\n", 58)

        elif instruction.opcode == 'STRI2INT':

            if data_second == None or data_third == None:
                my_exit("STRI2INT: Missing value\n", 56)

            if type(data_second) != str or type(data_third) != int:
                my_exit("Wrong operand types\n", 53)
            
            if data_third < 0 or data_third >= len(data_second):
                my_exit("Index out of boundaries of the string\n", 58)
            
            data_to_write = ord(data_second[data_third])

        elif instruction.opcode == 'READ':
            read_input = ""

            if input_f != None:
                if first_read:
                    input_data = read_lines(input_f)
                    first_read = False

                if len(input_data) == 0:
                    write_to_frame(nil_type, instruction.arguments[0], frames)
                    continue
                else:
                    read_input = input_data.pop(0)
            else:
                try:
                    read_input = input()
                except:
                    write_to_frame(nil_type, instruction.arguments[0], frames)
                    continue

            if data_second == "string":
                data_to_write = str(read_input)
            elif data_second == "int":
                try:
                    data_to_write = int(read_input)
                except:
                    data_to_write = nil_type
            elif data_second == "bool":
                if read_input.lower() == "true":
                    data_to_write = True;
                else:
                    data_to_write = False
            else:
                my_exit("Wrong instruction type for function READ\n", 57)

        elif instruction.opcode == 'WRITE':

            if data_first == None:
                my_exit("WRITE: Missing value\n", 56)
            if type(data_first) == bool:
                print(str(data_first).lower(), end="")
            else:
                print(data_first, end="")
            write_data = False

        elif instruction.opcode == 'CONCAT':

            if data_third == None or data_second == None:
                my_exit("CONCAT: Missing value\n", 56);

            if type(data_third) != str or type(data_second) != str:
                my_exit("Wrong operand types\n", 53)

            data_to_write = str(data_second) + str(data_third)

        elif instruction.opcode == 'STRLEN':

            if data_second == None:
                my_exit("STRLEN: Missing value\n", 56)
            if ( type(data_second) != str ):
                my_exit("Wrong operand types\n", 53)

            data_to_write = len(data_second)

        elif instruction.opcode == 'GETCHAR':

            if data_third == None or data_second == None:
                my_exit("GETCHAR: Missing value\n", 56);

            if type(data_second) != str or type(data_third) != int:
                my_exit("Wrong operand types\n", 53)
            
            if data_third < 0 or data_third >= len(data_second):
                my_exit(f"Index {data_third} out of boundaries of the string\n", 58)

            data_to_write = data_second[data_third]

        elif instruction.opcode == 'SETCHAR':

            if data_first == None or data_second == None or data_third == None:
                my_exit("SETCHAR: Missing value\n", 56)

            if type(data_second) != int or type(data_third) != str or type(data_first) != str:
                my_exit("Wrong operand types\n", 53)

            if (data_second < 0 or data_second >= len(data_first) or len(data_third) == 0):
                my_exit(f"Index {data_second} out of boundaries of the string {data_third}\n", 58)
            
            data_to_write = list(data_first)
            data_to_write[data_second] = data_third[0]
            data_to_write = "".join(data_to_write)

            
        elif instruction.opcode == 'TYPE':

            data_to_write = get_type(data_second)

        elif instruction.opcode == 'LABEL':
            
            write_data = False
            pass

        elif instruction.opcode == 'JUMP':

            write_data = False
            index = get_label_index(instruction.arguments[0],labels)

        elif instruction.opcode == 'JUMPIFEQ':

            write_data = False
            if data_third == None or data_second == None:
                my_exit("JUMPIFEQ: Missing value\n", 56)

            if type(data_third) == type(data_second) or data_third == nil_type or data_second == nil_type:
                if data_third == data_second:
                    index = get_label_index(instruction.arguments[0], labels)

                if str(instruction.arguments[0]) not in labels:
                    my_exit(f"Label {instruction.arguments[0]} was not defined\n", 52)
            else:
                my_exit("Wrong operand types\n", 53)

        elif instruction.opcode == 'JUMPIFNEQ':

            write_data = False
            if data_third == None or data_second == None:
                my_exit("JUMPIFNEQ: Missing value\n", 56)

            if type(data_third) == type(data_second) or data_third == nil_type or data_second == nil_type:
                if data_third != data_second:
                    index = get_label_index(instruction.arguments[0], labels)

                if str(instruction.arguments[0]) not in labels:
                    my_exit(f"Label {instruction.arguments[0]} was not defined\n", 52)
            else:
                my_exit("Wrong operand types\n", 53)

        elif instruction.opcode == 'EXIT':

            write_data = False
            if data_first == None:
                my_exit("EXIT: Missing value\n", 56);

            if type(data_first) != int:
                my_exit("Wrong operand types\n", 53)
            if data_first >= 0 and data_first <= 49:
                sys.exit(data_first)
            else:
                my_exit(f"Invalid exit number value '{data_first}'\n", 57)

        elif instruction.opcode == 'DPRINT':

            write_data = False
            print(data_first,file=sys.stderr,end="")

        elif instruction.opcode == 'BREAK':

            write_data = False
            sys.stderr.write(f"Index of current instruction: {index}\n")
            sys.stderr.write(f"Number of executed instructions: {executed_instructions}\n")
            sys.stderr.write(f"Global frame: {frames.GF}\n")
            sys.stderr.write(f"Local frame: {frames.LF}\n")
            sys.stderr.write(f"Temporary frame: {frames.TF}\n")

        if (write_data):
            write_to_frame(data_to_write, instruction.arguments[0], frames)


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
# read lines from source file
source_data = read_lines(source_f)
# use Element tree library to check if source data are correctly formated
root = XML_checker(source_data)
# check if instructions are in order or if header is present or 
# if they have correct number of arguments, etc.
root.check_xml_elements()
# read instructions from xml tree to a list for better manipulation
instructions = root.read_instructions()
check_argument_types(instructions)
labels = find_labels(instructions)
interpret(instructions, labels, input_f)
