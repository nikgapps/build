#!/sbin/sh

#################
# Initialization
#################

ps | grep zygote | grep -v grep >/dev/null && BOOTMODE=true || BOOTMODE=false
$BOOTMODE || ps -A 2>/dev/null | grep zygote | grep -v grep >/dev/null && BOOTMODE=true

umask 022

OUTFD=$2
ZIPFILE=$3
TMPDIR=/dev/tmp
COMMONDIR=$TMPDIR/NikGappsScripts
nikGappsLog=$TMPDIR/NikGapps.log

# echo before loading util_functions
ui_print() {
  echo "$1" >> "$nikGappsLog"
  if $BOOTMODE; then
    echo "$1"
  else
    echo -e "ui_print $1\nui_print" >> /proc/self/fd/$OUTFD
  fi
}

require_new_magisk() {
  ui_print "*******************************"
  ui_print " Please install Magisk v20.4+! "
  ui_print "*******************************"
  exit 1
}

if $BOOTMODE; then

  #########################
  # Load util_functions.sh
  #########################

  mount /data 2>/dev/null

  [ -f /data/adb/magisk/util_functions.sh ] || require_new_magisk
  . /data/adb/magisk/util_functions.sh
  [ $MAGISK_VER_CODE -lt 20400 ] && require_new_magisk
  install_module
  exit 0
else
  mkdir -p "$COMMONDIR"
  unzip -o "$ZIPFILE" customize.sh -d $COMMONDIR >&2
  [ -f $COMMONDIR/customize.sh ] && . $COMMONDIR/customize.sh
fi