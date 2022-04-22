<?php

// FUNCTION USED FOR HANDLING ERRORS RECEIVED BY PARAMETER $errorcode
function printError($errorcode) {
    switch ($errorcode) {
        case '10':
            error_log("Wrong combination/number of parameters\n");
            exit(10);
            break;
        case '11':
            error_log("Error opening file\n");
            exit(11);
            break;
        case '12':
            error_log("Error opening output file\n");
            exit(12);
            break;
        case '21':
            error_log("Header not found, different language or file is empty.\n");
            exit(21);
            break;
        case '22':
            error_log("Unknown/wrong machine code\n");
            exit(22);
            break;
        case '23':
            error_log("Lexical/syntactic error\n");
            exit(23);
            break;
    }
} 

// SUPPORTIVE FUNCTIONS USED FOR REGEX, ARGUMENT CHECKING
////////////////////////////////////////////////////////////////////////////////

// count($parsed) == 1(instruction) + arguments
// checks if instruction has the correct amount of arguments
function okCount($parsed, $suppCount ) {
    if (!(count($parsed) - 1 == $suppCount)) {
        printError(23);
    }
}

function convertXmlChars(&$varOrStr) {
    $varOrStr = preg_replace("/&/","&amp;", $varOrStr);
    $varOrStr = preg_replace("/</","&lt;", $varOrStr);
    $varOrStr = preg_replace("/>/","&gt;", $varOrStr);
}

////
// FUNCTIONS CHECKING EACH ARGUMENT TYPE
function checkVar($checkedVar){
    if (preg_match("/^(LF|TF|GF)@[A-ZÁ-Ža-zá-ž\-\*\$%_&#_&$%!?][A-ZÁ-Ža-zá-ž0-9\-\*\$%_&#_&$%!?]*$/", $checkedVar)) {
        convertXmlChars($checkedVar);
        return "var";
    } else {
        printError(23);
    }
}

function checkSymb(&$checkedSymb){
    if (preg_match("/^string@([^\\\#\s]*|\\\[0-9]{3})*$/", $checkedSymb)||
        preg_match("/^int@(\+|\-|[0-9])[0-9]*$/", $checkedSymb)||
        preg_match("/^bool@(true|false)$/", $checkedSymb)||
        preg_match("/^nil@nil$/", $checkedSymb)) {
        convertXmlChars($checkedSymb);
        return "const";
    } else if (preg_match("/^(LF|TF|GF)@[A-ZÁ-Ža-zá-ž\-\*\$%_&#_&$%!?][A-ZÁ-Ža-zá-ž0-9\-\*\$%_&#_&$%!?]*$/", $checkedSymb)) {
        convertXmlChars($checkedSymb);
        return "var";
    } else { 
        printError(23);
    }
}

function checkLabel($checkedLabel){
    if (preg_match("/^[A-ZÁ-Ža-zá-ž\-\*\$%_&#_&$%!?][A-ZÁ-Ža-zá-ž0-9\-\*\$%_&#_&$%!?]*$/", $checkedLabel)) {
        return "label";
    } else {
        printError(23);
    }
}

function checkType($checkedType) {
    if (preg_match("/^(string|bool|int)$/", $checkedType)) {
        return "type";
    } else {
        printError(23);
    }
}
////

// XML generator  
function generateCode($instrName, $order, $argType, $firstArg, $secondArg = null, $thirdArg = null) {
    
    echo(" <instruction order=\"$order\" opcode=\"$instrName\">"."\n");
    
    // first argument of the instruction
    switch($argType[0]) {
        case 'var':
            echo("  <arg1 type=\"var\">".trim($firstArg)."</arg1>"."\n");
            break;
        
        case 'const':
            $argument = explode('@', $firstArg, 2);
            echo("  <arg1 type=\"$argument[0]\">".$argument[1]."</arg1>"."\n");
            break;
        case 'label':
            echo("  <arg1 type=\"label\">".trim($firstArg)."</arg1>"."\n");
            break;
    }
    
    // second argument of the instruction
    if ($secondArg != null){
        switch($argType[1]) {
            case 'var':
                echo("  <arg2 type=\"var\">".trim($secondArg)."</arg2>"."\n");
                break;
            
            case 'const':
                $argument = explode('@',$secondArg,2);
                echo("  <arg2 type=\"$argument[0]\">".$argument[1]."</arg2>"."\n");
                break;
            case 'label':
                echo("  <arg2 type=\"label\">".trim($secondArg)."</arg2>"."\n");
                break;
            
            case 'type':
                echo("  <arg2 type=\"type\">".trim($secondArg)."</arg2>"."\n");
                break;
        }
        // third argument of the instruction
        if ($thirdArg != null) {
            switch($argType[2]) {
                case 'var':
                    echo("  <arg3 type=\"var\">".trim($thirdArg)."</arg3>"."\n");
                    break;
                
                case 'const':
                    $argument = explode('@',$thirdArg,2);
                    echo("  <arg3 type=\"$argument[0]\">".$argument[1]."</arg3>"."\n");
                    break;
                case 'label':
                    echo("  <arg3 type=\"label\">".trim($thirdArg)."</arg3>"."\n");
                    break;
            }
        }
    }
    echo(" </instruction>"."\n");
}

function getRidOfComments($commLine) {
    return(preg_replace("/ *#[\s\S]*$/","", $commLine));
}
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// ARGUMENT PARSING
////////////////////////////////////////////////////////////////////////////////
ini_set('display_errors', 'stderr');

if ($argc > 1){
    if ($argv[1] == "--help") {
        // too many arguments
        if ($argc > 2){
            printError(10);
        }
        // parse.php --help
        else {
            echo("usage: php parse.php < \"source file\"\n");
            exit(0);  
        }
    } else {
        printError(10);
    }
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// LANGUAGE, OPENING FILE VALIDITY
////////////////////////////////////////////////////////////////////////////////

// IGNORES EMPTY ROWS UNTIL IT MEETS SOMETHING, EVALUATES AND PRINTS ACCORDINGLY  
// CHECKS FOR FILE VALIDITY
while(1) {
    $line = fgets(STDIN);
    $line = getRidOfComments($line);
    $trimmedLine = trim($line);
    $try = 0;
    // error opening file
    if ($line === false && $try == 0) {
        printError(11);
    // file empty
    } else if ($line === false && $try != 0) {
        printError(21);
    }
    else if ($trimmedLine == '' || preg_match("/^ *#(\S|\s)*$/", $trimmedLine)) {
        continue;
    }
    // check if language is correct
    else {
        echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        
        if (strcasecmp($trimmedLine, '.IPPcode21') == 0){
            echo("<program language=\"IPPcode21\">\n");
            break;
        }
        // wrong language
        else {
            printError(21);
        }
    }
    $try++;
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// LINE PARSING 
////////////////////////////////////////////////////////////////////////////////

// counts instruction order
$order = 0;

while ($line = fgets(STDIN)) {
    $order++;
    
    // comment check
    $line = getRidOfComments($line);
    // replace excessive whitespace
    $line = preg_replace("/\h+/"," ",$line);
    // divide the lines into parts
    $lineParts = explode(" ", $line);
    // instruction names are case insensitive
    $lineParts[0] = strtoupper($lineParts[0]);
        
    // trimming before further parsing 
    foreach ($lineParts as &$element) {
        $element = trim($element);
    }
    unset($element);

    // FINITE AUTOMATA 
    // $lineparts[0] is the instruction name, 1-3 are arguments 
    switch ($lineParts[0]) {
        // INSTRUCTIONS WITH ONE ARGUMENT 
        case 'DEFVAR': //<var>
        case 'POPS': //<var>
            okCount($lineParts, 1);
            
            $type[0] = checkVar($lineParts[1]);
            
            generateCode($lineParts[0], $order, $type, $lineParts[1]);
            break;

        case 'PUSHS': //<symb>
        case 'WRITE': //<symb>
        case 'EXIT': //<symb>
        case 'DPRINT': //<symb>
            okCount($lineParts, 1);

            $type[0] = checkSymb($lineParts[1]);

            generateCode($lineParts[0], $order, $type, $lineParts[1]);
            break;

        case 'LABEL': //<label>
        case 'JUMP': //<label>
        case 'CALL': //<label>
            okCount($lineParts, 1);

            $type[0] = checkLabel($lineParts[1]);

            generateCode($lineParts[0], $order, $type, $lineParts[1]);
            break;

        // INSTRUCTIONS WITH TWO ARGUMENTS
        case 'MOVE': //<var> <symb>
        case 'INT2CHAR': //<var> <symb>
        case 'STRLEN': //<var> <symb>
        case 'NOT': //<var> <symb>
        case 'TYPE': //<var> <symb>
            okCount($lineParts, 2);
            
            $type[0] = checkVar($lineParts[1]);
            $type[1] = checkSymb($lineParts[2]);

            generateCode($lineParts[0], $order, $type, $lineParts[1], $lineParts[2]);
            break;
        
        case 'READ': //<var> <type>
            okCount($lineParts, 2);
            
            $type[0] = checkVar($lineParts[1]);
            $type[1] = checkType($lineParts[2]);

            generateCode($lineParts[0], $order, $type, $lineParts[1], $lineParts[2]);
            break;

        // INSTRUCTIONS WITH THREE ARGUMENTS
        case 'ADD': //<var> <symb> <symb>
        case 'SUB': //<var> <symb> <symb>
        case 'MUL': //<var> <symb> <symb>
        case 'IDIV': //<var> <symb> <symb>
        case 'LT': //<var> <symb> <symb>
        case 'GT': //<var> <symb> <symb>
        case 'EQ': //<var> <symb> <symb>
        case 'AND': //<var> <symb> <symb>
        case 'OR': //<var> <symb> <symb>
        case 'STRI2INT': //<var> <symb> <symb>
        case 'CONCAT': //<var> <symb> <symb>
        case 'GETCHAR': //<var> <symb> <symb>
        case 'SETCHAR': //<var> <symb> <symb>
            okCount($lineParts, 3);

            $type[0] = checkVar($lineParts[1]);
            $type[1] = checkSymb($lineParts[2]);
            $type[2] = checkSymb($lineParts[3]);

            generateCode($lineParts[0], $order, $type, $lineParts[1], $lineParts[2], $lineParts[3]);
            break;
        
        case 'JUMPIFEQ': //<label> <symb> <symb>
        case 'JUMPIFNEQ': //<label> <symb> <symb>
            okCount($lineParts, 3);

            $type[0] = checkLabel($lineParts[1]);
            $type[1] = checkSymb($lineParts[2]);
            $type[2] = checkSymb($lineParts[3]);
            
            generateCode($lineParts[0], $order, $type, $lineParts[1], $lineParts[2], $lineParts[3]);
            break;

        // INSTRUCTIONS WITHOUT ARGUMENTS
        case 'RETURN':
        case 'BREAK':
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
            okCount($lineParts, 0);
            
            echo(" <instruction order=\"$order\" opcode=\"$lineParts[0]\">\n");
            echo(" </instruction>\n");
            break;
        
        // EMPTY LINE -- NO INSTRUCTION -> $ORDER--
        case '':
            $order--;
            break;
        
        // DEFAULT CASE -- WRONG INSTRUCTION NAME
        default:
            printError(22);
    }
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
//SUCCESS
echo("</program>\n");
exit(0);
////////////////////////////////////////////////////////////////////////////////
?>