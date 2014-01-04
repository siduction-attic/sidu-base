#! /bin/bash
ANSWER=$1
APPL=$2
ARGS=$3
USER=$4
OPTS=$5
ARGS=$(echo $ARGS | sed -e "s/''//g")

CONFIG=/etc/sidu-base/shellserver.conf
test -f $CONFIG && source $CONFIG

test -n "$START_GUI_HOME" && export HOME=$START_GUI_HOME
test -d $HOME || export HOME=$START_GUI_HOME2

if [ -z "$CONSOLE" ] ; then
	CONSOLE=konsole
	CONSOLE_ARGS=
fi
which $CONSOLE || CONSOLE=x-terminal-emulator

test -n "$VERBOSE" && echo "startgui: user=$USER appl=$APPL opts=$OPTS console=$CONSOLE home=$HOME"

function Sux(){
	test -z "VERBOSE" || set -x
	USR=$1
	su -p --login -c "$2 $3 $4 $5 $6 $7 $8" $USR
	test -z "VERBOSE" || set +x
}
if [ -z "$DISPLAY" ] ; then
	export DISPLAY=:0
fi
FOUND=$(echo $OPTS | grep -i console)
if [ -z "$FOUND" ] ; then
	# sux $USER "$APPL" $ARGS
	Sux $USER "$APPL" $ARGS
else
	LINK=$(which $CONSOLE)
	while [ True ] ; do
		LINK=$(readlink $LINK)
		test -z "$LINK" && break
		if [ $(expr $LINK : "[.][.]") != 0 ] ; then
			LINK=/usr/bin/$LINK
		fi
		CONSOLE=$LINK
	done
	APPL2="$APPL"
	NODE=${CONSOLE##*/}
	test -z "$VERBOSE" && echo "terminal: $NODE"
	CONSOLE_ARGS=-e
	if [ $NODE = "qterminal" ] ; then
		CONSOLE_ARGS=
	fi
	if [ "$NODE" = "xfce4-terminal" -o "$NODE" = "qterminal" ] ; then
		if [ -n "$ARGS" ] ; then
			APPL2="$APPL $ARGS"
			ARGS=
		fi
	fi
	#sux $USER $CONSOLE $CONSOLE_ARGS "$APPL2" $ARGS
	Sux $USER $CONSOLE $CONSOLE_ARGS "$APPL2" $ARGS
	AGAIN=1
	while [ -n "$AGAIN" ] ; do
		#set -x
		AGAIN=$(ps aux | grep $APPL | grep -v grep | grep -v $0)
		#set +x
		sleep 1
	done
fi
echo $? >$ANSWER
chmod uog+w $ANSWER
echo $ANSWER ready!
