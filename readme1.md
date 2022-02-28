# Documentation of project implementation for 1. task IPP 2021/2022

Name and surname: Vaclav Korvas

Login: xkorva03

## Task

The main goal was to create a script to check if the given IPPcode22 is lexically and syntactically correct. And to print the XML representation of this code to STDOUT.

## Solution

The solution for the 1. task is split into 3 scripts (`parse.php, analyzer.php and generator.php`) and their functionality will be described later on. To write the correct representation of the code `XMLWriter` is used. The script has one optional parametr `--help`, which prints help and then the program exits any other argument causes error with exit code `10`.

### parse.php

This is the main script. The input is read line by line from STDIN and processed in a while loop. Firstly function
`proccess_line` is called. This function removes possible commentary and replaces all white characters wiht one
space. Then I check if correct IPPcode22 header is present. Then the code enters switch statement which determines what type of instruction was used. According to what instruction was used, functions from `analyzer.php` are called, to check if instruction arguments are lexically and syntactically correct.

### analyzer.php

This script contains function and regular expressions for syntax and lexical analysis. For every instruction argument (`<var>, <symb>, <type>, <label>`) is function and regular expression which checks if the arguments are correct. For the proper control I use built in function `preg_match` if the expression is incorrect the program will exit with syntax error `23`.

### generator.php

Functions from this script are used to generate correct representation of the IPPcode22. First function `start_xml` is called which sets correct encoding and creates the root element. Function`start_element` is used to create `instruction` element with given order and oppcode. Most of instruction arguments are created with function `write_instruction` except for `<symb>` argument because it can be either constant or variable, so for this argument I have created function `write_instruction_symb` which determines if I need to write constant or a variable.
