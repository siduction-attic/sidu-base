#! /bin/bash
# useful aliases and functions
# Recommandation: add "source /usr/share/sidu-base/backend/profile.sh" 
# at the end of your ~/.bashrc

if [ "$TERM" = "xterm" -o "$TERM" = "linux" ] ; then
        echo "loading $0..."
fi

alias lL='ls -ld'
alias lS='ls -ldSr'
alias lT='ls -ldtr'
alias ll='ls -ld'

alias lmg='lsmod | grep'

alias Fn='find -iname'

alias ap_i='apt-get install'
alias ap_p='apt-cache policy'
alias ap_s='apt-cache search'
alias ap_sh='apt-cache show'
alias ap_u='apt-get update'

alias e_exp='vi /etc/exports'
alias e_fs='vi /etc/fstab'
alias e_grp='vi /etc/group'
alias e_h='vi /etc/hosts'
alias e_smb='vi /etc/samba/smb.conf'

alias e_pl='vi /usr/share/sidu-manual/backend/profile.sh'

alias g_en="cd /etc/nginx"
alias g_ena="cd /etc/nginx/site-available"
alias g_ene="cd /etc/nginx/site-enabled"
alias g_l='cd /var/log/'
alias g_ln='cd /var/log/nginx'
alias g_ub="cd /usr/share/sidu-base"
alias g_ubb="cd /usr/share/sidu-base/backend"
alias g_ui="cd /usr/share/sidu-installer"
alias g_uib="cd /usr/share/sidu-installer/backend"
alias g_um="cd /usr/share/sidu-manual"
alias g_ud="cd /usr/share/sidu-disk-center"
alias g_vb="cd /var/cache/sidu-base"
alias sv_n="service nginx"

alias myip="ifconfig | perl -n -e 'print \"\$1\\n\" if /inet[ \\w]+:((\\d+\.){3}\\d+)\\s/ && \$1 ne \"127.0.0.1\";'"
alias o='less'

alias psg='ps aux | grep -v "grep -i" | grep -i'

function MkRepo {
	local DIR=$1
	if [ $DIR = "" ] ; then
		echo -e "Usage: MkRepo DIR\nMissing: DIR!"
	else
		pushd $DIR >/dev/null
		test -d debian || mkdir debian
		mv *.deb debian
		dpkg-scanpackages debian /dev/null | gzip -9 > Packages.gz
		echo "deb file:$DIR ./" >/etc/apt/sources.list.d/local.list
		apt-get update
		popd >/dev/null
		echo "Repo created: $DIR"
	fi
}

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


