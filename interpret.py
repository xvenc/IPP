import xml.etree.ElementTree as ET
import sys, getopt


class Instruction:

    def __init__(self, name : str, arguments, order : int):
        self.name = name
        self.arguments = arguments
        self.order = order

class Argument:

    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

def help():
    print("Usage: \tpython3 iterpret.py [--help] [--source=file , --input=file]")
    print("--help:\t Prints help. Cannot be used with other options.")
    print("--input=file: \tInput file with XML representation of source code. If not set, input is read from STDIN.")
    print("--source=file: \tFile with input used for interpretation of the code. If not set, intput read from STDIN")
    print("Atleast one of --source or --input needs to be set.")

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

def check_xml_elements(root):
     # CHECK if root has program attrib
    if (root.tag != "program"):
        sys.stderr.write("Wrong root tag.\n")
        exit(32)

    # loop through instructions
    for child in root:
        if ( child.tag != "instruction" ):
            sys.stderr.write("Wrong element tag, it should be instruction\n")
            exit(32)
        for attribute in child.attrib:
            if ( attribute not in ('opcode','order') ):
                sys.stderr.write("Wrong element attribute was used, should be 'order' or 'opcode'\n")
                exit(32)

        # loop through instruction arguments
        for args in child:
            if ( args.tag not in ('arg1','arg2','arg3') ):
                sys.stderr.write("Invalid arg tag number was used.\n")
                exit(32)

## MAIN CODE

input_f, source_f = check_args()
input_data = read_lines(input_f)
try:
    root = ET.fromstringlist(input_data)
except:
    sys.stderr.write("XML file wasnt well-formated.\n")
    exit(31)

check_xml_elements(root)

argument_l = []
arg1=Argument("var","GF@counter")
arg2=Argument("label","while")
argument_l.append(arg1)
argument_l.append(arg2)

inst = Instruction("MOVE",argument_l,1)
print(inst.arguments[0].typ)
