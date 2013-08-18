#! /bin/bash
test -n "$VERBOSE" && set -x
ANSWER=$1
CMD=$2
DISKS=$3
PHYSPART=$4
BOOT=$5
ROOT=$6
HOME=$7
SWAP=$8
perl autopart.pl "$CMD" "$ANSWER" "$DISKS" "$PHYSPART" "$BOOT" "$ROOT" "$HOME" "$SWAP"

