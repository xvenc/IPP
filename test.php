<?php

include 'html_generator.php';
// Global definitions of arguments
$interpret = "interpret.py";                // default interpret
$parse = "parse.php";                       // default parse 
$test_dir = "./";                           // default dir to search for tests
$jex_dir = "/pub/courses/ipp/jexamxml/";    // default dir to search for jexamxml.jar and options
$recursive = false;                         // variable to store if recursive option was set
$noclean = false;                           // variable to store if noclean option was set
$parse_only_set = FALSE;                    // if to do only parse tests
$int_only_set = FALSE;                      // if to do only interpret tests

$set_arguments = array();
$argument_regex = "((^--input=.+$)|(^--help$)|(^--directory=.+$)|(^--recursive$)|(^--parse-script=.+$)|(^--int-script=.+$)|(^--(parse|int)-only$)|(^--jexampath=.+$)|(^--noclean$))";
// function to print help
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

// fucntion to generate message on stderr and exit with given return code
function my_exit($text, $ret_code) {
    fwrite(STDERR, $text);
    exit($ret_code);
}

// function to parse command line paramets using php function getopt
function parse_arguments() {
    // list of all global variables
    global $interpret, $parse, $test_dir, $jex_dir, $recursive, $noclean, $parse_only_set,
           $int_only_set, $set_arguments, $argument_regex;
    $arg_array = array("help","directory:", "recursive", "parse-script:",
                       "int-script:", "parse-only", "int-only", "jexampath:", "noclean");
    
    # flags to ensure parse and interpret arguments are not combined
    $jexam_set = FALSE;
    $int_script_set = false;
    $parse_script_set = false;

    unset($_SERVER['argv'][0]);
    foreach($_SERVER['argv'] as $key => $value) {
        if (!preg_match($argument_regex, $value)) {
            my_exit("Wrong argument\n", 10);
        }    
    }
    // get all used long arguments
    $arguments = getopt("",$arg_array);
    
    // check for each indivudual option of the script
    if (array_key_exists("help", $arguments)) {
        if (count($arguments) != 1) {
            my_exit("ERROR: help argument cant be used with any other\n", 10);
        }
        my_help();
        exit(0);
    } 
    if (array_key_exists("directory", $arguments)){
        $test_dir = $arguments["directory"];
        array_push($set_arguments, "--directory");
        // check if directory exists
        if (!is_dir($test_dir)) {
            my_exit("Isnt a directory", 41);
        }

    } 

    if ( array_key_exists("recursive", $arguments) ) {
        $recursive = true;
        array_push($set_arguments, "--recursive");

    }
    if (array_key_exists("parse-script", $arguments)) {
        $parse = $arguments["parse-script"];
        $parse_script_set = true;
        array_push($set_arguments, "--parse-script");
        // check if file with parse.php exists
        if (!file_exists($parse)) {
            my_exit("File for parsing doesnt exists", 41);
        }

    } 
    if (array_key_exists("int-script", $arguments)) {
        $interpret = $arguments["int-script"];
        $int_script_set = true;
        array_push($set_arguments, "--int-script");
        // check if interpret file exists
        if (!file_exists($interpret)) {
            my_exit("File for interprettion doesnt exists", 41);
        }
    } 
    if (array_key_exists("parse-only", $arguments)) {
        $parse_only_set = true;
        array_push($set_arguments, "--parse-only");

    }  
    if (array_key_exists("int-only", $arguments)) {
        $int_only_set = true;
        array_push($set_arguments, "--int-only");

    } 
    if (array_key_exists("jexampath", $arguments)) {
        $jexam_set = true;
        $jex_dir = $arguments["jexampath"];
        if (!is_dir($jex_dir)) {
            my_exit("Not a directory with jexam", 41);
        }
        if (substr($jex_dir,-1) != "/") {
            $jex_dir = $jex_dir."/";
        }
        array_push($set_arguments, "--jexampath");
       
    }  
    if (array_key_exists("noclean", $arguments)) {
        $noclean = true;
        array_push($set_arguments, "--noclean");

    }

    # check if wrong combination of arguments wasnt used
    if ( ($int_only_set && $parse_only_set) || ($int_only_set && $jexam_set)
        || ($int_only_set && $parse_script_set) || ($parse_only_set && $int_script_set) ) {
        my_exit("Wrong combination of parametes was used\n", 11);
    }   

}

// function to check if all files (.rc, .out and .in) exists, if not create empty files
// except for .rc file, if .rc file doesnt exist then create one with ret code 0
function all_file_exists ($rc_file, $in_file, $out_file) {
    if (!file_exists($rc_file)) {
       $fp = fopen($rc_file, "w");
       fwrite($fp, "0"); 
       fclose($fp);
    }
    if (!file_exists($in_file)) {
        $fp = fopen($in_file, "w");
        fwrite($fp, "");
        fclose($fp);
    }
    if (!file_exists($out_file)) {
        $fp = fopen($out_file, "w");
        fwrite($fp, "");
        fclose($fp);
    }
}

// function to clean up all possible created files
function remove_tmp_files ($tmp_out, $tmp_xml, $xml_log) {
    if (file_exists($tmp_out)) {
        unlink($tmp_out);
    }
    if (file_exists($tmp_xml)) {
        unlink($tmp_xml);
    }
    // clean up log files after xml diff
    if (file_exists($xml_log)) {
        unlink($xml_log);
    }
}


# MAIN CODE

// parse program arguments
parse_arguments();

// determine if we search recursively all directories or just one directory
if ($recursive == false){
    try {
        $dir = new DirectoryIterator($test_dir);
    } catch (UnexpectedValueException) {
        my_exit("Directory doesnt exist\n", 41);
    }

} else {
    try {
        $dir = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($test_dir));
    } catch (UnexpectedValueException) {
        my_exit("Directory doesnt exist\n", 41);
    } 
}
// variables to store continuous results
$passed = 0;
$failed = 0;
$number = 0;

// generate HTML header with all configurations
if ($parse_only_set) {
    header_html("PARSE ONLY TESTS");
} elseif ($int_only_set) {
    header_html("INTERPRET ONLY TESTS");
} else {
    header_html("INTERPRET AND PARSE TESTS");
}



foreach ($dir as $file) {

    if ($file->getExtension() == "src" && ($file->getFilename()[0] != ".")) {
        $number++;
        $path = $file->getPathname();
        $path = substr($path, 0, -4);
        
        $rc_file = $path.".rc";             // file with correct return code
        $in_file = $path.".in";             // file with input for read instruction in interpret.py
        $out_file = $path.".out";           // file with correct output
        $tmp_out_file = $path."_tmp.out";   // help file for parse output
        $tmp_xml_out = $path."_xml.out";    // help file for xml diff
        $xml_log = $out_file.".log";

        // check if all necessary files exist, and if not then create them
        all_file_exists($rc_file, $in_file, $out_file);

        // get return code from .rc file, if more than one value then take the first one
        $exp_ret_code = intval(explode(" ",fgets(fopen($rc_file, 'r')))[0]);

        
        // do parse only tests
        if ($parse_only_set == true) {

            $parse_ret_code = 0;
            $jexjar = $jex_dir."jexamxml.jar";
            $jexopt = $jex_dir."options";

            # TODO change php -> php8.1
            $command = "php {$parse} < {$path}.src > {$tmp_out_file} 2> /dev/null";
            exec($command, $junk, $parse_ret_code); 
           // compare exit codes
            if ($parse_ret_code != 0 || $exp_ret_code != 0) {
                html_parse_only($number, $path.".src", $exp_ret_code, $parse_ret_code, "Wrong RC", "-");
                
            } else {
                // exit code is 0, do XML compare, need to compare xml files
                // check if all necessary files for jexamxml diff exists
                if (!is_file($jexjar) || !is_file($jexopt)) {
                    my_exit("File with jexamxml.jar or options doesnt exists", 41);
                }
                $xml_ret_code = 0;
                $xml_command = "java -jar {$jexjar} {$out_file} {$tmp_out_file} delta.xml /D {$jexopt} >/dev/null"; 
                exec($xml_command, $junk, $xml_ret_code);
                html_parse_only($number,$path.".src",$exp_ret_code, $xml_ret_code, "Wrong XML", "-");
            }
             
        // only interpret tests
        } elseif ($int_only_set == true) {
            $int_ret_code = 0;

            // command to be executed
            $command = "python3 {$interpret} --source={$path}.src --input={$in_file} > {$tmp_out_file} 2> /dev/null";
            exec($command, $junk, $int_ret_code); # TODO mby check if exec didnt failed

            // compare interpret return code with expected ret code
            if ($int_ret_code != 0 || $exp_ret_code != 0) {
                html_int_only($number, $path.".src", $exp_ret_code, $int_ret_code,"-", "Wrong RC");
                
            } else {
                // return code is correct
                // do diff on output and expected output
                $diff_ret_code = 0;
                $diff_command ="diff {$tmp_out_file} {$out_file} > /dev/null";
                exec($diff_command, $junk, $diff_ret_code);
                html_int_only($number, $path.".src", $exp_ret_code, $diff_ret_code,"-", "Wrong diff");

            }


        // Both parse and interpret tests
        } else {
            $int_ret_code = 0;
            $parse_ret_code = 0; 
            # TODO change php -> php8.1
            $parse_command = "php {$parse} < {$path}.src > {$tmp_xml_out} 2> /dev/null";
            $int_command = "python3 {$interpret} --source={$tmp_xml_out} --input={$in_file} > {$tmp_out_file} 2> /dev/null";
            $diff_command ="diff {$tmp_out_file} {$out_file} > /dev/null";

            exec($parse_command, $junk, $parse_ret_code);

            // check if parse failed
            if ($parse_ret_code != 0) {
                html_parse_only($number, $path.".src",0,$parse_ret_code, "WRONG RC", "NOT RUN");
                continue;
            } 
            // if parse failed the code wont be interpreted
            exec($int_command, $junk, $int_ret_code);
            if ($int_ret_code != 0 || $exp_ret_code != 0) {
                html_int_only($number, $path.".src", $exp_ret_code, $int_ret_code,"no", "Wrong RC");

            } else {
                $diff_ret_code = 0;
                exec($diff_command, $junk, $diff_ret_code);
                html_int_only($number, $path.".src", $exp_ret_code, $diff_ret_code,"no", "Wrong diff");
            }
        }

        // check if to clean or not to clean temporary files that were created
        if (!$noclean) {
            remove_tmp_files($tmp_out_file, $tmp_xml_out, $xml_log);
        }
    }
 }
 // generate html end and summary with number of passed and failed tests and succes rate
 html_end($number, $passed, $failed);
?>
