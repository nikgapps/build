########################################################
#
# NikGapps Survival Script for ROMs with addon.d support
# inspired from Magisk Survival Script by topjohnwu and osm0sis
#
########################################################

if [ -d "/postinstall" ]; then
  P="/postinstall/system"
  T="/postinstall/tmp"
else
  P="$S"
  T="/tmp"
fi
# Setup variables
recoveryLog=$T/recovery.log
recovery_tmp_log=/tmp/recovery.log
nikGappsDir="/sdcard/NikGapps"
addonLogsDir="$nikGappsDir/addonLogs"
NikGappsLog="$addonLogsDir/logfiles/NikGapps.log"
[ -n "$S" ] || S=/system
NikGappsTmpAddonDir=$T/addon.d/nikgapps
NikGappsAddonDir="$S/addon.d/nikgapps"
argument="$*"
execute_config=1
master_addon_file="50-nikgapps-addon.sh"
test "$ANDROID_ROOT" || ANDROID_ROOT=/system;
# Make Directories
mkdir -p "$NikGappsAddonDir"

addToLog() {
  if [ "$execute_config" = "1" ]; then
    mkdir -p "$(dirname "$NikGappsLog")";
    echo "$1" >> "$NikGappsLog"
  fi
}

ps | grep zygote | grep -v grep >/dev/null && BOOTMODE=true || BOOTMODE=false
$BOOTMODE || ps -A 2>/dev/null | grep zygote | grep -v grep >/dev/null && BOOTMODE=true
  if ! $BOOTMODE; then
    # update-binary|updater <RECOVERY_API_VERSION> <OUTFD> <ZIPFILE>
    OUTFD=$(ps | grep -v 'grep' | grep -oE 'update(.*) 3 [0-9]+' | cut -d" " -f3)
    [ -z $OUTFD ] && OUTFD=$(ps -Af | grep -v 'grep' | grep -oE 'update(.*) 3 [0-9]+' | cut -d" " -f3)
    # update_engine_sideload --payload=file://<ZIPFILE> --offset=<OFFSET> --headers=<HEADERS> --status_fd=<OUTFD>
    [ -z $OUTFD ] && OUTFD=$(ps | grep -v 'grep' | grep -oE 'status_fd=[0-9]+' | cut -d= -f2)
    [ -z $OUTFD ] && OUTFD=$(ps -Af | grep -v 'grep' | grep -oE 'status_fd=[0-9]+' | cut -d= -f2)
  fi
ui_print() { echo -e "ui_print $1\nui_print" >> /proc/self/fd/$OUTFD; }

beginswith() {
  case $2 in
  "$1"*)
    echo true
    ;;
  *)
    echo false
    ;;
  esac
}

CopyFile() {
  if [ -f "$1" ]; then
    mkdir -p "$(dirname "$2")"
    cp -f "$1" "$2"
    addToLog "- CopyFile: Copying $1 to $2"
  else
    addToLog "- File $1 does not exist!"
  fi
}

copy_logs() {
  ui_print "- Copying Logs at $argument"
  datetime=$(date +%Y_%m_%d_%H_%M_%S)
  nikGappsLogFile="NikGapps_addon_logs_$datetime.tar.gz"
  CopyFile "/etc/recovery.fstab" "$logDir/fstab/recovery.fstab"
  cd $addonLogsDir
  tar -cz -f "$T/$nikGappsLogFile" *
  cd /
  mkdir -p "$nikGappsDir"/logs
  CopyFile $T/"$nikGappsLogFile" "$nikGappsDir/logs/$nikGappsLogFile"
}

execute_addon() {
  mount /data 2>/dev/null
  if [ -d "$NikGappsAddonDir" ]; then
    if [ "$execute_config" = "1" ]; then
      ui_print "Executing $* in NikGapps addon"
      [ ! $BOOTMODE ] && test "$execute_config" = "1" && test "$mount_config" = "1" && test "$addon_version_config" = "2" && mount_partitions "product"
      test "$execute_config" = "1" && run_stage "$@"
      addToLog "- Copying recovery log at $argument"
      CopyFile "$recoveryLog" "$addonLogsDir/logfiles/recovery.log"
    else
      addToLog "! Execution disabled!"
    fi
  else
    ui_print "! Cannot find NikGapps addon - was data wiped or not decrypted?"
    exit 1
  fi
}

file_getprop() { grep "^$2=" "$1" | cut -d= -f2-; }

find_config() {
  if [ -f "/tmp/nikgapps.config" ]; then
    nikgapps_config_file_name="/tmp/nikgapps.config"
  elif [ -f "/sdcard1/nikgapps.config" ]; then
    nikgapps_config_file_name="/sdcard1/nikgapps.config"
  elif [ -f "/sdcard1/NikGapps/nikgapps.config" ]; then
    nikgapps_config_file_name="/sdcard1/NikGapps/nikgapps.config"
  elif [ -f "/sdcard/nikgapps.config" ]; then
    nikgapps_config_file_name="/sdcard/nikgapps.config"
  elif [ -f "/storage/emulated/NikGapps/nikgapps.config" ]; then
    nikgapps_config_file_name="/storage/emulated/NikGapps/nikgapps.config"
  elif [ -f "/storage/emulated/nikgapps.config" ]; then
    nikgapps_config_file_name="/storage/emulated/nikgapps.config"
  else
    nikgapps_config_file_name="$nikGappsDir/nikgapps.config"
  fi
}

find_slot() {
  slot=$(getprop ro.boot.slot_suffix 2>/dev/null)
  test "$slot" || slot=$(grep -o 'androidboot.slot_suffix=.*$' /proc/cmdline | cut -d\  -f1 | cut -d= -f2)
  if [ ! "$slot" ]; then
    slot=$(getprop ro.boot.slot 2>/dev/null)
    test "$slot" || slot=$(grep -o 'androidboot.slot=.*$' /proc/cmdline | cut -d\  -f1 | cut -d= -f2)
    test "$slot" && slot=_$slot
  fi
  test "$slot" && echo "$slot"
}

grep_cmdline() {
  local REGEX="s/^$1=//p"
  cat /proc/cmdline | tr '[:space:]' '\n' | sed -n "$REGEX" 2>/dev/null
}

# Check if the partition is mounted
is_mounted() {
  addToLog "- Checking if $1 is mounted"
  mount | grep -q " $1 ";
}

is_mounted_rw() {
  local mounted_rw=false
  local startswith=$(beginswith / "$1")
  test "$startswith" == "false" && part=/"$1" || part="$1"
  touch "$part"/.rw && rm "$part"/.rw && mounted_rw=true
  addToLog "- checked if $part/.rw is writable i.e. $mounted_rw ($1/.rw being original argument)"
  echo $mounted_rw
}

# Mount the partitions
mount_partitions() {
  local partitions="$*"
  # find the slot
  slot=$(find_slot)
  # the partition is not yet mounted as rw
  local part_mounted_rw=false
  local device_ab=$(getprop ro.build.ab_update 2>/dev/null);
  [ -z "$device_ab" ] && slot=""
  addToLog "- Current boot slot: $slot"
  for partition in $partitions; do
    # in case of A-only device $slot will be "" hence it can be used in conjunction with partitions
    if ! is_mounted "/$partition$slot"; then
      addToLog "- /$partition$slot not mounted, mounting..."
      if ! is_mounted "/$partition"; then
        addToLog "- /$partition is also not mounted!"
      else
        addToLog "- /$partition is mounted. unmounting..."
        # unmounting /$partition to mount again. This will ensure, the mounting is through this script!
        umount "$partition";
      fi
    else
      addToLog "- /$partition$slot already mounted, unmounting..."
      # unmounting /$partition$slot to mount again. This will ensure, the mounting is through this script!
      umount "$partition$slot";
    fi
    # this is for dynamic partitions where we have dedicated /product partition
    if [ "$(getprop ro.boot.dynamic_partitions)" = "true" ]; then
      if [ "$device_ab" = "true" ]; then
        addToLog "- Dynamic A/B device found, mounting /$partition$slot"
      else
        addToLog "- Dynamic A-Only device found, mounting /$partition"
      fi
      mount -o ro -t auto /dev/block/mapper/"$partition$slot" /"$partition" 2>/dev/null
      blockdev --setrw /dev/block/mapper/"$partition$slot" 2>/dev/null
      mount -o rw,remount -t auto /"$partition$slot" 2>/dev/null
      part_mounted_rw=$(is_mounted_rw "$partition$slot" 2>/dev/null)
    else
    # Now, we're in non-dynamic partitions where /product may or may not be dedicated
    # Also, Non dynamic A-only device may or may not have dedicated /product partition, hence mounting at once
      mount -o rw -t auto "/$partition" 2>/dev/null;
      if [ "$device_ab" = "true" ]; then
        addToLog "- Non Dynamic A/B device found, mounting /$partition"
        # there is no need for mounting /product since non-dynamic A/B don't have separate /product partition
        # instead, validating if /system/product is writable
        part_mounted_rw=$(is_mounted_rw "$partition" 2>/dev/null)
        if [ "$part_mounted_rw" = "false" ]; then
          # validating if /system/product is writable
          part_mounted_rw=$(is_mounted_rw "$S/$partition" 2>/dev/null)
        fi
      else
        addToLog "- Non Dynamic A-only device found, mounting /$partition"
        part_mounted_rw=$(is_mounted_rw "$partition" 2>/dev/null)
        if [ "$part_mounted_rw" = "false" ]; then
          # validating if /system/product is writable
          part_mounted_rw=$(is_mounted_rw "$S/$partition" 2>/dev/null)
        fi
      fi
    fi
    if [ "$part_mounted_rw" = "true" ]; then
      addToLog "- Mounted /$partition$slot successfully!"
    else
      addToLog "- Mounting /$partition$slot failed!"
#      exit
    fi
  done
}

# Read the config file from (Thanks to xXx @xda)
ReadConfigValue() {
  value=$(sed -e '/^[[:blank:]]*#/d;s/[\t\n\r ]//g;/^$/d' "$2" | grep "^$1=" | cut -d'=' -f 2)
  echo "$value"
  return $?
}

# Execute $NikGappsAddonDir/*.sh scripts with $1 parameter
run_stage() {
  [ $BOOTMODE ] && return
  if [ -d "$NikGappsTmpAddonDir"/ ]; then
    for script in $(find "$NikGappsTmpAddonDir"/ -name '*.sh' |sort -n); do
      $script "$1" "true"
    done
  else
    mkdir -p "/sdcard/NikGapps"
    echo "$NikGappsAddonDir doesn't exist" >> "/sdcard/NikGapps/addon_failed.log"
  fi
}

setup_env() {
  if [ ! "$(getprop 2>/dev/null)" ]; then
    getprop() {
      local propdir propfile propval;
      for propdir in / /system_root /system /vendor /odm /product; do
        for propfile in default.prop build.prop; do
          test "$propval" && break 2 || propval="$(file_getprop $propdir/$propfile $1 2>/dev/null)";
        done;
      done;
      test "$propval" && echo "$propval" || echo "";
    }
  elif [ ! "$(getprop ro.build.type 2>/dev/null)" ]; then
    getprop() {
      ($(which getprop) | grep "$1" | cut -d[ -f3 | cut -d] -f1) 2>/dev/null;
    }
  fi;
}

umount_all() {
  [ $BOOTMODE ] && return
  (if [ ! -d /postinstall/tmp ]; then
    ui_print "- Unmounting /system"
    umount /system;
    umount -l /system;
    if [ -e /system_root ]; then
      ui_print "- Unmounting /system_root"
      umount /system_root;
      umount -l /system_root;
    fi;
  fi;
  ui_print "- Unmounting /product"
  umount /product;
  umount -l /product;
  ) 2>/dev/null;
}

find_config

execute_config=$(ReadConfigValue "execute.d" "$nikgapps_config_file_name")
[ "$execute_config" != "0" ] && execute_config=1
addToLog "- execute_config = $execute_config"
unmount_config=$(ReadConfigValue "unmount.d" "$nikgapps_config_file_name")
[ "$unmount_config" != "0" ] && unmount_config=1
addToLog "- unmount_config = $unmount_config"
mount_config=$(ReadConfigValue "mount.d" "$nikgapps_config_file_name")
[ "$mount_config" != "0" ] && mount_config=1
addToLog "- mount_config = $mount_config"
addon_version_config=$(ReadConfigValue "addon_version.d" "$nikgapps_config_file_name")
[ -z "$addon_version_config" ] && addon_version_config=2
addToLog "- addon_version_config = $addon_version_config"

if [ "$execute_config" = "0" ]; then
  rm -rf $S/addon.d/$master_addon_file
  rm -rf $S/addon.d/nikgapps
  rm -rf $T/addon.d/$master_addon_file
  rm -rf $T/addon.d/nikgapps
  exit 1
fi

# Copy the addon file to ensure
if [ ! -f "$S/addon.d/$master_addon_file" ]; then
  addToLog "- Copying $0 to $S/addon.d/$master_addon_file at $argument"
  test "$execute_config" = "1" && CopyFile "$0" "$S/addon.d/$master_addon_file"
else
  test "$execute_config" = "1" && addToLog "- $S/addon.d/$master_addon_file already present at $argument"
fi

# Store the current storage details of partitions
mkdir -p "$addonLogsDir/partitions"
df > "$addonLogsDir/partitions/size_at_$1.txt"
df -h > "$addonLogsDir/partitions/size_readable_at_$1.txt"
ls -alR /system > "$addonLogsDir/partitions/System_Files_at_$1.txt"
ls -alR /product > "$addonLogsDir/partitions/Product_Files_at_$1.txt"

setup_env

case "$1" in
  pre-backup)
    # keep GApps addon.d from executing unless GApps are actually installed
    if [ ! -f /system/etc/g.prop ]; then
      rm -f /postinstall/tmp/addon.d/69-gapps.sh
      rm -f $T/addon.d/69-gapps.sh
      rm -f $T/addon.d/70-gapps.sh
    fi
    rm -rf $addonLogsDir
    rm -rf $NikGappsLog
    execute_addon "$@"
  ;;
  backup)
    execute_addon "$@"
    [ ! $BOOTMODE ] && test "$execute_config" = "1" && test "$addon_version_config" = "2" && umount /product
  ;;
  post-backup)
    # Stub
  ;;
  pre-restore)
    # Stub
  ;;
  restore)
    execute_addon "$@"
    addToLog "- Restoring NikGapps addon scripts"
    test "$execute_config" = "1" && cp -a $T/addon.d/nikgapps/* $S/addon.d/nikgapps/
    [ ! $BOOTMODE ] && test "$execute_config" = "1" && test "$unmount_config" = "1" && umount_all
    test "$execute_config" = "1" && copy_logs
    rm -rf $addonLogsDir
  ;;
  post-restore)
  ;;
esac
