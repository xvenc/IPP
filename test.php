<?php

# Global definitions of arguments
$interpret = "interpret.py";
$parse = "parse.php";
$test_dir = "./";
$jex_dir = "./pub/courses/ipp/jexamxml/";
$recursive = false;
$noclean = false;
$parse_only_set = FALSE;
$int_only_set = FALSE;

function my_help() {
    echo "Usage: php8.1 test.php [options]\n\n";
    echo "Options:\n\n";
    echo "--help:\t\t\tPrints this help\n";
    echo "--directory=path:\ttests will search in given directory. (default is this directory)\n";
    echo "--recursive:\t\ttests will search in given directory recursivelly in all its subdirectories\n";
    echo "--parse-script=file:\tfile with php script to analyze source code in IPPcode22. (default is parse.php, in this directory)\n";
    echo "--int-script=file:\tfile with python script to interpret XML representation of IPPcode22. (default is interpret.py in this directory)\n";
    echo "--parse-only:\t\ttests only parser, dont combine with --int-only and --int-script\n";
    echo "--int-only:\t\ttests only interpretation script, dont combine with --parse-only, parse-script and --jexampath\n";
    echo "--jexampath=path:\tpath to directory containing jexamxml.rar file\n";
    echo "--noclean:\t\ttest.php wont delete files created during testing\n";
}

function my_exit($text, $ret_code) {
    fwrite(STDERR, $text);
    exit($ret_code);
}

function parse_arguments() {
    global $interpret, $parse, $test_dir, $jex_dir, $recursive, $noclean, $parse_only_set,
           $int_only_set;

    $arg_array = array("help","directory:", "recursive", "parse-script:",
                       "int-script:", "parse-only", "int-only", "jexampath:", "noclean");
    
    # flags to ensure parse and interpret arguments are not combined
    $jexam_set = FALSE;
    $int_script_set = false;
    $parse_script_set = false;

    $arguments = getopt("",$arg_array);
    if (array_key_exists("help", $arguments)) {
        if (count($arguments) != 1) {
            my_exit("ERROR: help argument cant be used with any other\n", 10);
        }
        my_help();
        exit(0);

    } 
    if (array_key_exists("directory", $arguments)){
        $test_dir = $arguments["directory"];

    } 
    if ( array_key_exists("recursive", $arguments) ) {
        $recursive = true;

    }
    if (array_key_exists("parse-script", $arguments)) {
        $parse = $arguments["parse-script"];
        $parse_script_set = true;
        
    } 
    if (array_key_exists("int-script", $arguments)) {
        $interpret = $arguments["int-script"];
        $int_script_set = true;

    } 
    if (array_key_exists("parse-only", $arguments)) {
        $parse_only_set = true;

    }  
    if (array_key_exists("int-only", $arguments)) {
        $int_only_set = true;

    } 
    if (array_key_exists("jexampath", $arguments)) {
        $jexam_set = true;
        $jex_dir = $arguments["jexampath"];
        
    }  
    if (array_key_exists("noclean", $arguments)) {
        $noclean = true;
    }

    # control if wrong combination of arguments wasnt used
    if ( ($int_only_set && $parse_only_set) || ($int_only_set && $jexam_set)
        || ($int_only_set && $parse_script_set) || ($parse_only_set && $int_script_set) ) {
        my_exit("Wrong combination of parametes was used\n", 11);
    }   
}

function rc_file_exists ($rc_file, $path) {
    if (file_exists($path)) {

    }
}

# MAIN CODE

parse_arguments();
# if recursive change to recursive directory iterator
if ($recursive == false){
    $dir = new DirectoryIterator($test_dir);

} else {
    $dir = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($test_dir));
    
}

foreach ($dir as $file) {

    if ($file->getExtension() == "src" && !$file->isDot() && ($file->getFilename()[0] != ".")) {
        // echo $file->getFilename()."\n";
        $path = $file->getPathname();
        $path = substr($path, 0, -4);
        $name = $file->getBasename('.'.$file->getExtension()); 
        $rc_file = $name.".rc";
        $in_file = $name.".in";
        $out_file = $name.".out";

        rc_file_exists($rc_file, $path.".rc");
        if ($parse_only_set) {
            # TODO only parse.php tests
            
        }


    }

 }


?>