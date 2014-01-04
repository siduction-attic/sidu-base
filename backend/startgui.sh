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
	CONSOLE_ARGS=-e
fi
which $CONSOLE || CONSOLE=x-terminal-emulator

test -n "$VERBOSE" && echo "startgui: user=$USER appl=$APPL opts=$OPTS console=$CONSOLE home=$HOME"

if [ -z "$DISPLAY" ] ; then
	export DISPLAY=:0
fi
FOUND=$(echo $OPTS | grep -i console)
if [ -z "$FOUND" ] ; then
	su -p --login $USER "$APPL" $ARGS
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
	echo "terminal: $NODE"
	if [ "$NODE" = "xfce4-terminal" -o "$NODE" = "qterminal" ] ; then
		if [ -n "$ARGS" ] ; then
			APPL2="$APPL $ARGS"
			ARGS=
		fi
	fi
	su -p --login $USER $CONSOLE $CONSOLE_ARGS "$APPL2" $ARGS
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
