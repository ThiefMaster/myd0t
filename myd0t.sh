#!/bin/sh

if type shopt > /dev/null 2>&1; then
	shopt -s xpg_echo
fi

red="\033[1;31m"
green="\033[1;32m"
yellow="\033[1;33m"
reset="\033[0m"

install_python3() {
	if type apt > /dev/null 2>&1; then
		echo 'Using apt (debian/ubuntu)'
		apt update && apt install python3
	elif type dnf > /dev/null 2>&1; then
		echo 'Using dnf (fedora)'
		dnf install python3
	elif type yum > /dev/null 2>&1; then
		echo 'Using yum (centos)'
		yum install python3
	elif type pacman > /dev/null 2>&1; then
		echo 'Using pacman (arch)'
		pacman -Sy python3
	else
		echo "${red}No known package manager found :(${reset}"
		echo 'aborting'
	fi
	# XXX: no need to handle gentoo here; it always has python installed
}

if ! type python3 > /dev/null 2>&1; then
	echo
	echo "${yellow}This installer requires python3, which is not installed.${reset}"
	if [ "$(id -u)" != "0" ]; then
		echo 'Please install it and then re-run this installer.'
		exit 1
	fi
	choices="${green}Y${reset}/${red}n${reset}"
	echo "Install it automatically using your distribution's package manager? [$choices] "
	read choice
	case "$choice" in
		y|Y|yes|'')
			install_python3
			;;
		*)
			echo 'aborting'
			exit 1
			;;
	esac
fi

./myd0t.py "$@"
