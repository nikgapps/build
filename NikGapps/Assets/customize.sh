DEBUG=true
SKIPUNZIP=1

# File Defaults
ZIPDIR=$(dirname "$ZIPFILE")
ZIPNAME="$(basename "$ZIPFILE")"

if $BOOTMODE; then
  COMMONDIR=$MODPATH/NikGappsScripts
  mkdir -p "$COMMONDIR"
fi

# Prop file potential locations
PROPFILES="/system/default.prop /system/build.prop /system/product/build.prop /vendor/build.prop /product/build.prop /system_root/default.prop /system_root/build.prop /system_root/product/build.prop /data/local.prop /default.prop /build.prop"

# Partition size defaults
system_ext_size=0
product_size=0
system_size=0

# Partition variables
system="/system"
product=""
system_ext=""
dynamic_partitions="false"
TMPDIR=/dev/tmp

# Logs
NikGappsAddonDir="/system/addon.d/nikgapps"
datetime=$(date +%Y_%m_%d_%H_%M_%S)
nikGappsLogFile="NikGapps_logs_$datetime.tar.gz"
recoveryLog=/tmp/recovery.log
logDir="$TMPDIR/NikGapps/logs"
nikGappsDir="/sdcard/NikGapps"
nikGappsLog=$TMPDIR/NikGapps.log
busyboxLog=$TMPDIR/busybox.log
addonDir="$TMPDIR/addon"
sdcard="/sdcard"

addToLog() {
  echo "$1" >>"$nikGappsLog"
}

ensure_config() {
  mkdir -p "$nikGappsDir"
  mkdir -p "$addonDir"
  mkdir -p "$logDir"
  nikgappsConfig="$sdcard/NikGapps/nikgapps.config"
  debloaterConfig="$sdcard/NikGapps/debloater.config"
  if [ ! -f $nikgappsConfig ]; then
    unpack "afzc/nikgapps.config" "/sdcard/NikGapps/nikgapps.config"
    [ ! -f "/sdcard/NikGapps/nikgapps.config" ] && unpack "afzc/nikgapps.config" "/storage/emulated/NikGapps/nikgapps.config"
    addToLog "nikgapps.config is copied to $nikgappsConfig"
  fi
  if [ ! -f $debloaterConfig ]; then
    unpack "afzc/debloater.config" "/sdcard/NikGapps/debloater.config"
    [ ! -f "/sdcard/NikGapps/debloater.config" ] && unpack "afzc/debloater.config" "/storage/emulated/NikGapps/debloater.config"
    addToLog "debloater.config is copied to $debloaterConfig"
  fi
}

unpack() {
  mkdir -p "$(dirname "$2")"
  addToLog "- unpacking $1"
  addToLog "  -> to $2"
  unzip -o "$ZIPFILE" "$1" -p >"$2"
  chmod 755 "$2";
}

unpack "common/nikgapps_functions.sh" "$COMMONDIR/nikgapps_functions.sh"
unpack "common/unmount.sh" "$COMMONDIR/unmount.sh"
unpack "common/mount.sh" "$COMMONDIR/mount.sh"
unpack "common/device.sh" "$COMMONDIR/device.sh"
unpack "common/install.sh" "$COMMONDIR/install.sh"
unpack "common/file_size" "$COMMONDIR/file_size"
unpack "common/addon" "$COMMONDIR/addon"
unpack "common/header" "$COMMONDIR/header"
unpack "common/functions" "$COMMONDIR/functions"
unpack "common/nikgapps.sh" "$COMMONDIR/nikgapps.sh"

# load all NikGapps functions
. "$COMMONDIR/nikgapps_functions.sh"
# find device details
. "$COMMONDIR/device.sh"
# unmount for a fresh install
. "$COMMONDIR/unmount.sh"
# mount all the partitions
. "$COMMONDIR/mount.sh"

df > "$COMMONDIR/size_before.txt"
df -h > "$COMMONDIR/size_before_readable.txt"
copy_file "$COMMONDIR/size_before.txt" "$logDir/partitions/size_before.txt"
copy_file "$COMMONDIR/size_before_readable.txt" "$logDir/partitions/size_before_readable.txt"
nikGappsLogo
addToLog "- stock busybox version: $(busybox | head -1)"
setup_flashable
[ -n "$actual_file_name" ] && ui_print "- File Name: $actual_file_name"
find_zip_type
begin_unmounting
begin_mounting
ensure_config
find_config
# find device information
show_device_info
# find if the device has dedicated partition or it's symlinked
find_partition_type
# find whether the install type is dirty or clean
test "$zip_type" != "debloater" && find_install_type
# check if partitions are mounted as rw or not
check_if_partitions_are_mounted_rw
ls -alR /system >"$logDir/partitions/System_Files_Before.txt"
ls -alR /product >"$logDir/partitions/Product_Files_Before.txt"
# fetch available system size
find_system_size
# find the size required to install gapps
find_gapps_size
# run the debloater
test "$zip_type" = "debloater" && debloat
calculate_space "system" "product" "system_ext"
ui_print " "
test "$zip_type" == "addon_exclusive" || test "$zip_type" == "addon" && is_on_top_of_nikgapps
test "$zip_type" = "debloater" && ui_print "--> Starting the debloat process"

if [ "$zip_type" != "debloater" ]; then
  ui_print "--> Starting the install process"
fi

. "$COMMONDIR/install.sh"
