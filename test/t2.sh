#!/bin/bash
TOP_DIR=$(cd $(dirname "$0") && pwd)
VERBOSE="yes"

# ===== FUNCTIONS =============================================================
# this function writes a message to the console in the format:
# YYYY-MM-DD HH:MM:SS: module [thead_id]: <level> <str>
# called: msgout "INFO" "message string"
msgout() {
    local xtrace
    xtrace=$(set +o | grep xtrace)
    set +o xtrace

    local level=$1
    local str=$2
    local tm
    tm=`date +"%Y-%m-%d %H:%M:%S"`
    if [ "$level" == "DEBUG" ] && [ -z "$VERBOSE" ]; then
        $xtrace
        return 0
    else
        echo "$tm: $PROG [$$]: $level: $str"
    fi
    $xtrace
}

prgm_exit() {
    local retc=$1
    local display_complete_msg=$2
    local endtm=$(date +"%s%3N")
    local e=$(( endtm - STARTTM ))
    local elapsed_in_secs=$(awk -v m=$e 'BEGIN { print (m / 1000) }')

    if [ -z $display_complete_msg ]; then
        msgout "INFO" "$PROG Completed in $elapsed_in_secs seconds"
    fi
    echo " "
    exit $retc
}
# ***** START **************************************************
if [ "$#" >= 1 ]; then
    threads=1
else
    threads=$1
fi
if [ "$#" != 2 ]; then
    iterations=1
else
    iterations=$2
fi

msgout "INFO" "Starting......."
for (( a=0; a < $threads; a++ )); do
    echo "====== thread: $a"
    $TOP_DIR//t1.sh $iterations &
    sleep .5
done

prgm_exit 0 ''
