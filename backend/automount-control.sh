#!/bin/sh
# Switches automounting on or off (for gnome)
#set -x
date "+%Y.%m.%d %H:%M:%S: $1" >>/tmp/automount.log

[[ ! -x /usr/bin/gsettings ]] && exit 2

if [ -f /etc/default/distro ]; then
    . /etc/default/distro
fi

#if [ ! -f /etc/default/fll-gnome-desktop ]; then
session=$(pgrep -u "${FLL_LIVE_USER}" session)
export $(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$session/environ)
#test -z $VERBOSE || echo "DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"
#fi


case "$1" in
    enabled)
	ENABLE_AUTOMOUNT=true
        ;;
    disabled)
	ENABLE_AUTOMOUNT=false
        ;;
    *)
        echo "automount-control.sh called with unknown argument \`$1'" >&2
        exit 1
        ;;
esac


case "$FLL_FLAVOUR" in
    gnome)
        su ${FLL_LIVE_USER} -c "gsettings set org.gnome.desktop.media-handling automount-open $ENABLE_AUTOMOUNT"
        ;;
    cinnamon)
        ###su ${FLL_LIVE_USER} -c "gsettings set org.gnome.desktop.media-handling automount-open true"
	;;
esac

#set +x


