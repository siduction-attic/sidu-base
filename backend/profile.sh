#! /bin/bash
export HOST=$(hostname)
export HOME_PREMIUM_USER=/home/hm

if [ `expr $PATH : ".*/home/bin/lnk"` = 0 ] ; then
        export PATH=/home/bin/lnk:$PATH:/usr/local/bin
fi
if [ "$DISPLAY" != "" -a "$USER" != root ]; then 
	xauth merge /home/$USER/.Xauthority
fi
export HOST=`hostname`
FIRST_PROFILE=/home/bin/std/local.profile
test -e $FIRST_PROFILE || FIRST_PROFILE=/usr/local/bin/local.profile
test -e $FIRST_PROFILE || FIRST_PROFILE=/usr/share/sidu-base/backend/profile.sh

if [ "$TERM" = "xterm" -o "$TERM" = "linux" ] ; then
	echo "loading $FIRST_PROFILE..."
fi
PATH_FIRST_PROFILE=$(dirname $FIRST_PROFILE)
SECOND_PROFILE=/home/bin/$HOST/local.profile
test -e $SECOND_PROFILE || SECOND_PROFILE=FIRST_PROFILE
PATH_SECOND_PROFILE=$(dirname $SECOND_PROFILE)
if [ -z "$EDITOR" ] ; then
	export EDITOR=vi
fi

alias ap_i="apt-get install"
alias ap_s="apt-cache search"
alias ap_sh="apt-cache show"
alias ap_p="apt-cache policy"
alias ap_u="apt-get update"

alias g_ulb="cd /usr/local/bin"
alias lm="lsmod | grep"
alias ll="ls -ld"
alias "e_pl=$EDITOR $SECOND_PROFILE"
alias ss="sudo -s"
alias g_en="cd /etc/nginx"
alias g_ena="cd /etc/nginx/sites-available"
alias g_ap2="cd /etc/apache2/sites-available"
alias e_ap2="vi /etc/apache2/sites-available/000-default.conf"
alias g_bin="cd /home/bin"
alias g_binl="cd $PATH_SECOND_PROFILE"
alias g_bins="cd $PATH_FIRST_PROFILE"
alias g_ini="cd /etc/init.d"
alias g_log="cd /var/log/"
alias g_nga="cd /etc/nginx/sites-available"

alias c_m="cat /proc/mdstat"
alias n_g="netstat -tulpn | grep -i"

alias e_ps="vi /home/bin/$HOST/$HOST.profile"
alias e_ps="vi /home/bin/std/local.profile"
alias e_smb="vi /etc/samba/smb.conf"
alias e_fs="vi /etc/fstab"
alias e_h="vi /etc/hosts"
alias e_exp="vi /etc/exports"
alias e_pw="vi /etc/passwd"
alias e_grp="vi /etc/group"

alias a_i="apt-get install"
alias a_s="apt-cache search"

alias psg='ps aux | grep -v "grep -i" | grep -i'
alias lmg="lsmod | grep"
alias myip="ifconfig | perl -n -e 'print \"\$1\\n\" if /((\\d+\.){3}\\d+)\\s/ && \$1 ne \"127.0.0.1\";'"
alias o=less
alias g_ini="cd /etc/init.d"

alias i_i="/etc/init.d/$1 $*"

alias lT="ls -ldtr"
alias lL="ls -ld"
alias lS="ls -ldSr"

alias Fn="find -iname"

alias g_ub="cd /usr/share/sidu-base"
alias g_ubb="cd /usr/share/sidu-base/backend"
alias g_vb="cd /var/cache/sidu-base"
alias g_vbs="cd /var/cache/sidu-base/shellserver-tasks"
alias P="ln -sf /usr/share/sidu-base/backend/profile.sh"

function s_agent()
{
    SUDO=sudo
    X=$(ps aux | grep "ssh-agent.*dbus" | grep -v grep | head -n 1)
    if [ -n "$X" -o  "$1" == "first" ] ; then
    	killall -9 ssh-agent
    fi
    if ps -o "%p %c" -u `id -u` |grep ssh-agent; then
       set $(ps -o "%p %c" -u $(id -u)|grep ssh-agent )
       SSH_AGENT_PID=$1
       export SSH_AGENT_PID
       SSH_AUTH_SOCK=$($SUDO find /tmp/ -type s -name "agent.$(( $1 - 1 ))" -uid $(id -u))
       export SSH_AUTH_SOCK
       echo "ssh-agent lief bereits"
   else
       eval $(ssh-agent )
       FN=.ssh/id_dsa
       if [ ! -f $FN ] ; then FN=~/.ssh/id_rsa ; fi
       ssh-add $FN
       echo "ssh-agent wurde gestartet"
   fi
}
if [ $(id -u) == "0" ] ; then
	export HOME=$HOME_PREMIUM_USER
fi
test $SECOND_PROFILE != $FIRST_PROFILE && source $SECOND_PROFILE

