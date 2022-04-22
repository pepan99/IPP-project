<?php


function printhtml($passed, $failed, $testnames, $returnValues, $returnValuesInt, $returnValuesPar, $success, $parseOnly, $intOnly) {
    echo("<!DOCTYPE html>
    <html>
    <head>
    <title>IPP - test.php</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <meta name=\"description\" content=\"Testování parse.php a/nebo interpret.py.\">
    <style>
    body {background-color:#ffffff;background-repeat:no-repeat;background-position:top left;background-attachment:fixed;}
    h1{font-family:Arial, sans-serif;color:#000000;background-color:#ffffff;}
    p {font-family:Georgia, serif;font-size:14px;font-style:normal;font-weight:normal;color:#000000;
    </style>
    </head>
    <body>
    <h1>Výsledky testů:</h1>");
    echo("<hr />");
    for($i = 0; $i< count($testnames); $i++) {
        echo("<p>");echo($testnames[$i]."</p>");
        echo("
        ");
        echo("<p>Očekávaný návratový kód: <strong>".$returnValues[$i]."</strong></p>");
        echo("<p>Získaný návratový kód <strong>");
        if ($parseOnly) {
            echo($returnValuesPar[$i]."</strong></span></p>");
        } else {
            echo($returnValuesInt[$i]."</strong></span></p>");
        }
        if ($success[$i]){
            echo("<p><span>Výsledek testu: </span><span style= \"color:#00FF00;\"><strong>"."ÚSPĚCH"."</strong></span></span></p>");
        } else {
            echo("<p><span>Výsledek testu: </span><span style = color:#FF0000;\"><strong>"."NEÚSPĚCH"."</strong></span></span></p>");
        }
        echo("<hr />");

    }    
    echo("<hr />
    ");
    echo("<p>Počet úspěšných testů: <span style=\"color:#00FF00;\"><strong>");
    echo($passed); echo("</strong></span></p>");

    echo("<p>Počet neúspěšných testů: <span style=\"color:#FF0000;\"><strong>");
    echo($failed); 
    echo("</strong></span></p>");

    echo("<p>Celkový počet testů: <strong>");echo(count($testnames));echo("</strong></p>");

    echo("</body>
    </html>");
// }
}

## returns array of adresses of files 
function recursiveSearch($address, &$counter, &$field, $isRecursive) {
    if (is_dir($address)) {
        $files1 = scandir($address);
        foreach($files1 as $file1) {
                $openFile = "$address"."/$file1";
                if (!preg_match("/\./", $file1) && $isRecursive) {
                    recursiveSearch($openFile, $counter, $field);
                }
                elseif (preg_match("/.src$/", $file1)){
                        $field[$counter] = $openFile;
                        $counter++;
                    }
                
            
        }
    }
    else {
        if (preg_match("/.src$/", $address)){
            $openFile = "$address";
            $field[$counter] = $openFile;
            $counter++;
        }
    }
}

function sortFound(&$array, &$in1, &$out1, &$src1, &$rc1) {
    $srcCounter = 0; 
    foreach($array as $each) {
        $fileName = explode(".src",$each); 
        $src1[$srcCounter] = $fileName[0].'.src';
        if (!file_exists($fileName[0].'.in')) {
            file_put_contents($fileName[0].'.in', '');
        }
        if (!file_exists($fileName[0].'.out')) {
            file_put_contents($fileName[0].'.out', '');
            
        }
        if (!file_exists($fileName[0].'.rc')) {
            file_put_contents($fileName[0].'.rc', '0');
        }
        $in1[$srcCounter] = $fileName[0].'.in';
        $out1[$srcCounter] = $fileName[0].'.out';
        $rc1[$srcCounter] = $fileName[0].'.rc';
        $srcCounter++;
    } 
}

$directory = './';
$recursive = FALSE;
$parseScript = './parse.php';
$parseScriptOn = FALSE;
$intScript = './interpret.py';
$intScriptOn = FALSE;
$parseOnly = FALSE;
$intOnly = FALSE;
#$jexamxl = '/jexamxml.jar';
$jexamxl = '/pub/courses/ipp/jexamxml/jexamxml.jar';
#$jexamxl = '/options';
$jexamcfg = ' /pub/courses/ipp/jexamxml/options';

$getOpt = getopt('',array('help','directory:','recursive', 'parse-script:'));

if (array_key_exists('help', $getOpt)) {
    if($argc == 2) {
    echo("This is a test file used for testing of parse.php and interpret.py\n\n");
    echo("Usage:  --help | prints this message, can't be combined with other arguments\n
        --directory=path | path to searched tests\n
        --recursive | recursively find all tests in subdirectories\n
        --parse-script=file | script file used for IPPcode21 analysis\n
        --int-script=file | script file used running instructions from XML \n
        --parse-only | run tests on parse.php only\n
        --int-only | run tests on interpret.py only\n
        --jexamxml | path to jexamxml file\n
        --jexamcfg | path to jexam config file \n
        --recursive | recursively find all tests in subdirectories\n");
    exit(0);
    }
    else {
        exit(10);
    }
} 
if (array_key_exists('directory', $getOpt)) {
    $directory = $getOpt["directory"];
}
if (array_key_exists('recursive', $getOpt)) {
    $recursive = TRUE;
}
if (array_key_exists('parse-script', $getOpt)) {
    $parseScript = $getOpt["parse-script"];
    $parseScriptOn = TRUE;
}
if (array_key_exists('int-script', $getOpt)) {
    $intScript= $getOpt["int-script"];
    $intScriptOn = TRUE;
}
if (array_key_exists('parse-only', $getOpt)) {
    $parseOnly= TRUE;
    print('aaaa');
}
if (array_key_exists('int-only', $getOpt)) {
    $intOnly= TRUE;
}
if (array_key_exists('jexamxml', $getOpt)) {
    $jexamxl= $getOpt["jexamxml"];
}
if (array_key_exists('jexamcfg', $getOpt)) {
    $jexamcfg= $getOpt["jexamcfg"];
}
if ($parseOnly && $intOnly || $parseOnly && $intScriptOn || $intOnly && $parseScriptOn) {
    exit(10);
}
$fieldOfFiles = array();

$counter = 0;

recursiveSearch($directory, $counter, $fieldOfFiles, $recursive);

$testnames = array();
$returnValues = array();
$returnValuesInt = array();
$returnValuesPar = array();
$success = array();
$in = array();
$out = array();
$src = array();
$rc = array();

sortFound($fieldOfFiles, $in, $out, $src, $rc);

$output = array();
$failed = 0;
$passed = 0;
//php 7.4 ./parse.php < ./ipp_tests/parse-only/GENERATED/add/simple00.src > compare.test 2>&1 
// echo($src[0]."\n");
// echo($rc[0]."\n");
// echo($out[0]."\n");

for($i = 0; $i< count($src); $i++) {
    $output='';

    if ($parseOnly) {
        exec("php7.4 ".$parseScript." <".$src[$i]." > compare.test 2>/dev/null", $output, $returnValPar);
        exec("java -jar ".$jexamxl." ".$out[$i]." compare.test ".$jexamcfg, $output, $diff);
    } elseif ($intOnly) {
        exec("python3.8 ".$intScript." --source=".$src[$i]." --input=".$in[$i]." > python.test 2>/dev/null", $output, $returnValInt);#2>&1
        $diff = exec("diff ".$out[$i]." python.test");
    } else {
        exec("php7.4 ".$parseScript." <".$src[$i]." > compare.test 2>/dev/null", $output, $returnValPar);
        exec("python3.8 ".$intScript." --source="."compare.test"." --input=".$in[$i]." > python.test 2>/dev/null", $output, $returnValInt);#2>&1
        $diff = exec("diff ".$out[$i]." python.test");
    }

    $retcode = file_get_contents($rc[$i], true, null);

    array_push($returnValues,$retcode);
    array_push($returnValuesPar,$returnValPar);
    array_push($returnValuesInt,$returnValInt);

        if ($returnValInt == $retcode){
            if ($returnValInt == 0) { 
                if ($diff == 0) {
                    $passed++;
                    array_push($success,TRUE);
                } else {
                    $failed++;
                    array_push($success,FALSE);
                }
            } else {
                $passed++;
                array_push($success,TRUE);
            }
        }
        else {
            $failed++;
            array_push($success,FALSE);
        }
}

printhtml($passed, $failed, $src, $returnValues, $returnValuesInt, $returnValuesPar, $success, $parseOnly,$intOnly);

?>