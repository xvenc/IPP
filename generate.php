<?php

// write new xml instruction of given type and with given arg number
function write_instruction(string $text, string $type, string $arg) {
    global $xw;
    xmlwriter_start_element($xw, $arg);
    xmlwriter_write_attribute($xw, "type", $type);
    xmlwriter_text($xw, $text);
    xmlwriter_end_element($xw); // arg1
}

// write symbol instruction, decides if its variable or constatnt
function write_instruction_symb(string $text,string $option, string $arg) {
    global $xw;
    if ( $option == "var") {
        // its a variable
        xmlwriter_start_element($xw, $arg);
        xmlwriter_write_attribute($xw, "type", $option);
        xmlwriter_text($xw, $text);
        xmlwriter_end_element($xw); // arg11

    } else {
        // its constatnt
        $text = explode("@",$text);
        xmlwriter_start_element($xw, $arg);
        xmlwriter_write_attribute($xw,"type", $text[0]);
        xmlwriter_text($xw, $text[1]);
        xmlwriter_end_element($xw); //arg1
    } 
}

// start new instruction element
function start_element(string $instr, string $instr_cnt) {
    global $xw;
    xmlwriter_start_element($xw, "instruction");
    xmlwriter_write_attribute($xw, "order", $instr_cnt);
    xmlwriter_write_attribute($xw, "opcode", $instr);
    return;
}

function start_xml()  {
    global $xw;
    xmlwriter_set_indent($xw, 1);
    $res = xmlwriter_set_indent_string($xw, '  ');
    xmlwriter_start_document($xw, '1.0', 'UTF-8');

    // start new program element
    xmlwriter_start_element($xw,"program");
    xmlwriter_write_attribute($xw,"language","IPPcode22");
}

?>