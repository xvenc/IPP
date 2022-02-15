<?php
include 'error.php';
include 'analyzer.php';

// remove commentary and white characters from beggining and end of the line
// and replace all whitespace characters with single space
function proccess_line(string $line) : string {
    $line = trim($line);
    $line = preg_replace('/\s+/', ' ', $line);
    $line = explode("#",$line)[0];
    return trim($line);
}

function check_header(string $first_line) {
    if (strtoupper($first_line) != ".IPPCODE22") {
        fprintf(STDERR,"ERRPR: Missing header.\n");
        exit(21);
    }
}

// main code
if ($argc == 2) {
    if ($argv[1] == "--help") {
        print_help();
    } else {
        fprintf(STDERR,"ERROR: Wrong parametrs were used.\n");
        exit(10);
    } 
} 

$header = false;
$instruction_cnt = 0;

$dom = new DOMDocument('1.0','UTF-8');
$dom->formatOutput = true;
$prog = $dom->createElement("program");
$prog->setAttribute("language",".IPPcode22");
$dom->appendChild($prog);

// loop through every line of the input file
while(($line = fgets(STDIN)) !== FALSE) {

    // remove commentary
    $line = proccess_line($line);
    
    // check if its not an empty line
    if (trim($line) == "") continue;

    // check if .IPPcode22 header is present
    if (!$header) {
        check_header($line);
        $header = true;
        continue;
    }

    

    // instructions are case insensitive so I need to make them upper
    $line = explode(" ", $line);
    $instruction = strtoupper($line[0]);

    $xml_ins = $dom->createElement("instruction");

    switch($instruction) {

        // instructions with 0 opperands
        case "RETURN":
        case "BREAK":
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
            if (count($line) == 1) {
                $instruction_cnt++;
                $xml_ins->setAttribute("order", $instruction_cnt);
                $xml_ins->setAttribute("opcode",$instruction);
                $prog->appendChild($xml_ins);
            } else {
                exit(23);
            }
        break; 
        
        // instructions with 1 opperand <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            if (count($line) == 2) {
                check_label($line[1]);
            } else {
                exit(23);
            }
        break;
        
        // instructions with 1 opperand <var>
        case "DEFVAR":
        case "POPS":
            if (count($line) == 2) {
                check_var($line[1]);
                $instruction_cnt++;
                $xml_ins->setAttribute("order", $instruction_cnt);
                $xml_ins->setAttribute("opcode", $instruction);
                $arg1 = $dom->createElement("arg1",$line[1]);
                $arg1->setAttribute("type","var");
                $xml_ins->appendChild($arg1);
                $prog->appendChild($xml_ins);
            } else {
                exit(23);
            }
        break;


        // instruction with 1 operand <symb>
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            if (count($line) == 2) {
                check_symb($line[1]);
            } else {
                exit(23);
            }
        break;

        // instructions with 2 opperands <var> <symb>

        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
        case "NOT":

            if (count($line) == 3) {
                check_var($line[1]);
                check_symb($line[2]);
            } else {
                exit(23);
            }
        break;

        // instructions with 2 operands <var> <type>

        case "READ":
            if (count($line) == 3) {
                check_var($line[1]);
                check_type($line[2]);
            } else {
                exit(23);
            }
        break;

        // instructions with 3 operands <var> <symb1> <symb2>

        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STR2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            if (count($line) == 4) {
                check_var($line[1]);
                check_symb($line[2]);
                check_symb($line[3]);
            } else {
                exit(23);
            }
        break;

        // instruictions with 3 operands <label> <symb1> <symb2>

        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            if (count($line) == 4) {
                check_label($line[1]);
                check_symb($line[2]);
                check_symb($line[3]);
            } else {
                exit(23);
            }
        break;

        default:
            exit(22);
    }
    //echo "\n";
}
// print xml representation of the code
echo $dom->saveXML();
?>