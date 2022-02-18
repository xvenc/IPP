<?php
include 'analyzer.php';
include 'generate.php';

// remove commentary and white characters from beggining and end of the line
// and replace all whitespace characters with single space
function proccess_line(string $line) : string {
    $line = trim($line);
    $line = preg_replace('/\s+/', ' ', $line);
    $line = explode("#",$line)[0];
    return trim($line);
}

// check if correct header is present
function check_header(string $first_line) {
    if (strtoupper($first_line) != ".IPPCODE22") {
        //fprintf(STDERR,"ERROR: Missing header.\n");
        exit(21);
    }
}
// print simple help if parametr --help is used
function print_help() {
    echo "Usage:\nphp parser.php [--help] < IPPcode22\n";
    echo "Parametrs:\n";
    echo "--help\t Prints this help\n";
    exit(0);
}


// START OF THE MAIN CODE
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

// start of xml writer document
$xw = xmlwriter_open_memory();
start_xml();

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


    switch($instruction) {
        // instructions with 0 opperands
        case "RETURN":
        case "BREAK":
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
            if (count($line) == 1) {
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                xmlwriter_end_element($xw); // instruction
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
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction($line[1], "label", "arg1");
                xmlwriter_end_element($xw); //instruction
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
                start_element($instruction, $instruction_cnt);   
                write_instruction($line[1], "var", "arg1");
                xmlwriter_end_element($xw); //instruction
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
                $option = check_symb($line[1]);
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction_symb($line[1], $option, "arg1");
                xmlwriter_end_element($xw); //instruction
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
                $option = check_symb($line[2]);
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction($line[1], "var", "arg1");
                write_instruction_symb($line[2], $option, "arg2");
                xmlwriter_end_element($xw); //instruction
            } else {
                exit(23);
            }
        break;

        // instructions with 2 operands <var> <type>
        case "READ":
            if (count($line) == 3) {
                check_var($line[1]);
                check_type($line[2]);
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction($line[1], "var", "arg1");
                write_instruction($line[2], "type", "arg2");
                xmlwriter_end_element($xw); //instruction
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
                $option1 = check_symb($line[2]);
                $option2 = check_symb($line[3]);
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction($line[1], "var", "arg1");
                write_instruction_symb($line[2], $option1, "arg2");
                write_instruction_symb($line[3], $option2, "arg3");
                xmlwriter_end_element($xw);
            } else {
                exit(23);
            }
        break;

        // instruictions with 3 operands <label> <symb1> <symb2>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            if (count($line) == 4) {
                check_label($line[1]);
                $option1 = check_symb($line[2]);
                $option2 = check_symb($line[3]);
                $instruction_cnt++;
                start_element($instruction, $instruction_cnt);
                write_instruction($line[1], "label", "arg1");
                write_instruction_symb($line[2], $option1, "arg2");
                write_instruction_symb($line[3], $option2, "arg3");
                xmlwriter_end_element($xw);
            } else {
                exit(23);
            }
        break;

        default:
            exit(22);
    } // case

} // while

// print xml representation of the code
xmlwriter_end_element($xw); //program
xmlwriter_end_document($xw);
echo xmlwriter_output_memory($xw);
?>