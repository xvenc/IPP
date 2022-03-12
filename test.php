<?php

include 'html_generator.php';
# Global definitions of arguments
$interpret = "interpret.py";
$parse = "parse.php";
$test_dir = "./";
$jex_dir = "./pub/courses/ipp/jexamxml/"; # TODO change it when testing on merlin
$recursive = false;
$noclean = false;
$parse_only_set = FALSE;
$int_only_set = FALSE;

$argv = array();
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
           $int_only_set, $argv;
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
        array_push($argv, "--directory");

    } 
    if ( array_key_exists("recursive", $arguments) ) {
        $recursive = true;
        array_push($argv, "--recursive");

    }
    if (array_key_exists("parse-script", $arguments)) {
        $parse = $arguments["parse-script"];
        $parse_script_set = true;
        array_push($argv, "--parse-script");

        // TODO check if script exists 
    } 
    if (array_key_exists("int-script", $arguments)) {
        $interpret = $arguments["int-script"];
        $int_script_set = true;
        array_push($argv, "--int-script");

        // TODO check if script exists
    } 
    if (array_key_exists("parse-only", $arguments)) {
        $parse_only_set = true;
        array_push($argv, "--parse-only");

    }  
    if (array_key_exists("int-only", $arguments)) {
        $int_only_set = true;
        array_push($argv, "--int-only");

    } 
    if (array_key_exists("jexampath", $arguments)) {
        $jexam_set = true;
        $jex_dir = $arguments["jexampath"];
         array_push($argv, "--jexampath");
       
    }  
    if (array_key_exists("noclean", $arguments)) {
        $noclean = true;
        array_push($argv, "--noclean");

    }

    # control if wrong combination of arguments wasnt used
    if ( ($int_only_set && $parse_only_set) || ($int_only_set && $jexam_set)
        || ($int_only_set && $parse_script_set) || ($parse_only_set && $int_script_set) ) {
        my_exit("Wrong combination of parametes was used\n", 11);
    }   

}

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

function remove_tmp_files ($tmp_out, $tmp_xml) {
    // Clean up created files
    if (file_exists($tmp_out)) {
        unlink($tmp_out);
    }
    if (file_exists($tmp_xml)) {
        unlink($tmp_xml);
    }
}


# MAIN CODE

parse_arguments();

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
$passed = 0;
$failed = 0;
$number = 0;
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
        //echo $file->getFilename()."\n";
        $path = $file->getPathname();
        $path = substr($path, 0, -4);
        
        $rc_file = $path.".rc";
        $in_file = $path.".in";
        $out_file = $path.".out";
        $tmp_out_file = $path."_tmp.out"; # help file for parse output
        $tmp_xml_out = $path."_xml.out";

        $exp_ret_code = intval(explode(" ",fgets(fopen($rc_file, 'r')))[0]);

        // check if all necessary files exist
        all_file_exists($rc_file, $in_file, $out_file);

        if ($parse_only_set) {
            $parse_ret_code = 0;

            $command = "php {$parse} < {$path}.src > {$tmp_out_file} 2> /dev/null";
            exec($command, $junk, $parse_ret_code); 

           // compare exit codes
            if ($parse_ret_code != 0 || $exp_ret_code != 0) {
                html_parse_only($number, $path.".src", $exp_ret_code, $parse_ret_code, "Wrong RC", "-");
                
            } else {
                // exit code is 0, do XML compare
                $xml_ret_code = 0;
                $xml_command = "java -jar {$jex_dir} {$out_file} {$tmp_out_file} tests/ipp-2022-tests/options >/dev/null"; 
                exec($xml_command, $junk, $xml_ret_code);
                html_parse_only($number,$path.".src",$exp_ret_code, $xml_ret_code, "Wrong XML", "-");
            }
             

        } elseif ($int_only_set) {
            // only interpret tests
            $int_ret_code = 0;

            $command = "python3 {$interpret} --source={$path}.src --input={$in_file} > {$tmp_out_file} 2> /dev/null";
            exec($command, $junk, $int_ret_code); # TODO mby check if exec didnt failed

            if ($int_ret_code != 0 || $exp_ret_code != 0) {
                html_int_only($number, $path.".src", $exp_ret_code, $int_ret_code,"-", "Wrong RC");
                
            } else {
                // do diff on output and expected output
                $diff_ret_code = 0;
                $diff_command ="diff {$tmp_out_file} {$out_file} > /dev/null";
                exec($diff_command, $junk, $diff_ret_code);
                html_int_only($number, $path.".src", $exp_ret_code, $diff_ret_code,"-", "Wrong diff");

            }


        } else {
            // Both parse and interpret tests
            $int_ret_code = 0;
            $parse_ret_code = 0; 
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

        if (!$noclean) {
            remove_tmp_files($tmp_out_file, $tmp_xml_out);
        }
    }

 }
 html_end($number, $passed, $failed);
?>