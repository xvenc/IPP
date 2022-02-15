<?php

$reg_bool = "/^bool@(true|false)/";
$reg_int = "/^int@([+-]?[0-9])+/";
$reg_string = "/^string@([^\\\]|\\\[0-9][0-9][0-9])*$/";
$reg_nil = "/nil@nil/";

$reg_var = "/^(TF|GF|LF)@[A-Za-z_\-$&%*!?][A-Za-z0-9_\-$&%*!?]*$/";
$reg_label = "/^[A-Za-z_\-$&%*!][\w_\-$&%*!*]*$/";
$reg_type = "/(int|bool|string)/";

function check_label(string $label) {
    global $reg_label;
    if ( preg_match($reg_label,$label) ) {
//        echo "label ";
    } else {
        exit(23);
    }
}

function check_var(string $variable) {
    global $reg_var;
    if ( preg_match($reg_var,$variable) ) {
//        echo "var ";
    } else {
        exit(23);
    }
}

function check_symb(string $symbol) {
    global $reg_var, $reg_bool, $reg_int, $reg_nil, $reg_string;
    // check if its constant or variable
    if ( preg_match("~^(int|string|bool|nil)~", $symbol) && (preg_match($reg_bool, $symbol) || 
        preg_match($reg_string, $symbol) || 
        preg_match($reg_int, $symbol) || 
        preg_match($reg_nil, $symbol)) ) {
        // its a constatnt
  //      echo "const ";
    } elseif (preg_match($reg_var, $symbol)) {
        // it a var
//        echo "symb var ";
    } else {
        exit(23);
    }
}

function check_type(string $type) {
    global $reg_type;
    if ( preg_match($reg_type, $type) ) {
       // echo "type ";        
    } else {
        exit(23);
    }
}
?>