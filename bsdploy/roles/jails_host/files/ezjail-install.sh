#!/bin/sh

# Make it clear in code very early, that we're working on the whole system
cd /

# Hard code base jail's position for now
ezjail_jaildir=/usr/jails
ezjail_jailbase=${ezjail_jaildir}/basejail
ezjail_jailtemplate=${ezjail_jaildir}/newjail

# define our bail out shortcut
exerr () { echo -e "$*" >&2 ; exit 1; }

# Create ezjail's working directory
mkdir -p /usr/local/etc/ezjail || exerr "Error: Check your permissions"

# Define list of directories in base jail
ezjail_basejail_dirlist="/bin /boot /lib /libexec /rescue /sbin /usr/bin /usr/include /usr/lib /usr/libdata /usr/libexec /usr/sbin /usr/src /usr/share"
ezjail_templatejail_dirlist="/dev /etc /media /mnt /proc /root /tmp /var"
case `uname -p` in amd64) ezjail_dirlist="${ezjail_dirlist} /usr/lib32";; esac


# cpio creates directories with strange permissions. Fix them before hand
mkdir -p "${ezjail_jailbase}/usr"

# Create mount point in new template
mkdir -p "${ezjail_jailtemplate}/usr/local" "${ezjail_jailtemplate}"/basejail

# loop over all directories for the new base system
for dir in ${ezjail_basejail_dirlist}; do
  find ${dir} | cpio -d -p -v "${ezjail_jailbase}" || exerr "Error: Installation of ${dir} failed."
  ln -s /basejail/${dir} "${ezjail_jailtemplate}"/${dir}
done

# loop over all directories for template dir
for dir in ${ezjail_templatejail_dirlist}; do
  find ${dir} | cpio -d -p -v "${ezjail_jailtemplate}" || exerr "Error: Installation of ${dir} failed."
done
