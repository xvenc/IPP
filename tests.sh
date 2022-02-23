#!/bin/bash

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'

TESTS='tests/ipp-2022-tests'
PARSE_TESTS="$TESTS/parse-only/"
JEXAMXML_PATH="$TESTS/jexamxml.jar"
JEXAMXML_OPT_PATH="$TESTS"

echo -e "${ORANGE}PARSE-ONLY${NC}"
for DIR in $(ls $PARSE_TESTS)
do
    echo -e "  ${CYAN}$DIR${NC}"
    for TEST_NAME in $(ls $PARSE_TESTS/$DIR | grep ".src")
    do
        TEST_NAME=${TEST_NAME%.*}
        echo -e -n "\t${BLUE}$TEST_NAME:${NC}"

        php parse.php < "$PARSE_TESTS/$DIR/$TEST_NAME.src" > tmp
        RETVAL=$?
        RETVAL_EXPECTED=$(cat "$PARSE_TESTS/$DIR/$TEST_NAME.rc")

        # check if return codes match
        if [ $RETVAL != $RETVAL_EXPECTED ]; then
            echo -e " ${RED}FAILED${NC}"
        else
            if [ $RETVAL != 0 ]; then
                # error occured, no need to do XML_DIFF
                echo -e " ${GREEN}PASSED${NC}"
            else
                # no error occured, do XML_DIFF
                XML_EXP=$PARSE_TESTS/$DIR/$TEST_NAME.out
                java -jar $JEXAMXML_PATH tmp $XML_EXP $JEXAMXML_OPT_PATH/options>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e " ${GREEN}PASSED${NC}"
                else
                    echo -e " ${RED}FAILED${NC}"
                fi
            fi
        fi
    done
done

rm -rf tmp*
