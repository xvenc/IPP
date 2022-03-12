<?php
// TODO create array with number of failed test
function html_parse_only($number,$path, $expected, $RC, $parse_err, $int_err) {
    global $passed, $failed;
    if ($expected == $RC) {
        echo"<tr class=\"passed\">
            <td>$number</td>
            <td>$path</td>
            <td>no</td>
            <td>$int_err</td>
            <td>$expected</td>
            <td>$RC</td>
            <td> PASSED </td>
        </tr>"."\n";
        $passed++;
    } else {
        echo"<tr class=\"failed\">
            <td>$number</td>
            <td>$path</td>
            <td>$parse_err</td>
            <td>$int_err</td>
            <td>$expected </td>
            <td>$RC</td>
            <td> FAILED </td>
        </tr>"."\n";
        $failed++;
    } 
}

function html_int_only($number,$path, $expected, $RC, $parse_err, $int_err) {
    global $passed, $failed;
    if ($expected == $RC) {
        echo"<tr class=\"passed\">
            <td>$number</td>
            <td>$path</td>
            <td> $parse_err </td>
            <td> no </td>
            <td>$expected</td>
            <td>$RC</td>
            <td> PASSED </td>
        </tr>"."\n";
        $passed++;
    } else {
        echo"<tr class=\"failed\">
            <td>$number</td>
            <td>$path</td>
            <td> $parse_err </td>
            <td> $int_err </td>
            <td>$expected </td>
            <td>$RC</td>
            <td> FAILED </td>
        </tr>"."\n";
        $failed++;
    } 
}

function header_html($test_type) {
    global $argv;
    $list = implode( ", ", $argv ); 
    echo "<!DOCTYPE html>
    <html lang=\"cz\">
    <head>
        <title>IPPcode22 test results</title>
        <style>
            body { font-family: 'Times New Roman', Times, serif;
                background-color: #282828;
                color:#ebdbb2
                }
            .failed {background-color:#fb4934; color:#282828}
            .passed {background-color:#b8bb26; color: #282828}
            h1 {text-align: center;}
    
            table {
                border: 1px solid #ebdbb2;
                text-align: center;
                padding: 5px;
            }
            th {
                border: 1px solid #ebdbb2;
                padding: 5px;
            }
            td {
                border: 1px solid #ebdbb2;
                padding: 5px;
            }
            tr:hover {
                background-color: #458588;
            }
            p {text-align: center;}
            h4 {text-align: center;}
            .center {
                margin-left: auto;
                margin-right: auto;
            }
            .summary {
                margin-left: auto;
                margin-right: auto;
                width: 30%;
                font-size: 20px;
            }
        </style>
    </head>
    <body>
    
    <h1>IPPcode22 test results</h1>
    
    <h4>test.php was run with these parametrs: $list</h4>
    <table class=\"center\">
        <tr style=\"font-weight: bold; background-color: #83a598; color: #282828;\">
            <th colspan=\"7\">$test_type</th>
        </tr>
        <tr>
            <th>Number</th>
            <th>Path</th>
            <th>parse error</th>
            <th>interpret error</th>
            <th>Expected</th>
            <th>Return code</th>
            <th>Status</th>
        </tr>"."\n";
}


function html_end($number, $passed, $failed) {
    $result = round($passed/$number * 100, 2);
    echo "</table><br><br>"."\n";
    echo "<table class=\"summary\">
    <tr style=\"background-color: #83a598; color: #282828;  height: 50px;\">
        <th colspan=\"2\">SUMMARY</th>
    </tr>
    <tr height: 50px;>
        <th>Number of tests</th>
        <td>$number</td>
    </tr>
    <tr height: 50px;>
        <th>Sucessfull tests</th>
        <td style=\"color: #b8bb26;\">$passed</td>
    </tr>
    <tr height: 50px;>
        <th>Failed tests</th>
        <td style=\"color: #fb4934;\">$failed</td>
    </tr>
    <tr style=\"background-color: #b8bb26; color: #282828; height: 50px;\">
        <th>Sucess rate</th>
        <td style=\"font-weight: bold;\">$result %</td>
    </tr>
</table>"."\n";
    echo "
    </body>
    </html>
     "."\n";
}
?>