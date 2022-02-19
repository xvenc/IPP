import xml.etree.ElementTree as ET
import sys, getopt

input_f=''
source_f=''

def help():
    print("Usage: \tpython3 iterpret.py [--help] [--source=file , --input=file]")
    print("--help:\t Prints help. Cannot be used with other options.")
    print("--input=file: \tInput file with XML representation of source code. If not set, input is read from STDIN.")
    print("--source=file: \tFile with input used for interpretation of the code. If not set, intput read from STDIN")
    print("Atleast one of --source or --input needs to be set.")


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
# debug
print(input_f)
print(source_f)
