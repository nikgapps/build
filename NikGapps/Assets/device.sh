#!/sbin/sh

get_available_size() {
    df=$(df -k /"$1" | tail -n 1)
    case $df in
        /dev/block/*) df=$(echo "$df" | awk '{ print substr($0, index($0,$2)) }');;
    esac
    free_system_size_kb=$(echo "$df" | awk '{ print $3 }')
    echo "$free_system_size_kb"
}

get_block_for_mount_point() {
  fstab_file_path="/vendor/etc/fstab.$(getprop ro.boot.hardware)"
  [ ! -f "$fstab_file_path" ] && fstab_file_path="/etc/recovery.fstab" && addToLog "- Vendor fstab doesn't exist!"
  [ -n "$2" ] && fstab_file_path="$2"
  grep -v "^#" "$fstab_file_path" | grep " $1 " | tail -n1 | tr -s ' ' | cut -d' ' -f1
}

find_block() {
  local name="$1"
  local fstab_entry=$(get_block_for_mount_point "/$name")
  # P-SAR hacks
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/")
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/system_root")
  addToLog "- fstab_entry of $name is $fstab_entry with BLK_PATH $BLK_PATH"
  # if $fstab_entry is blank, we shall try to find the block in recovery fstab
  [ -z "$fstab_entry" ] && fstab_entry=$(get_block_for_mount_point "/$name" "/etc/recovery.fstab") \
    && addToLog "- recovery fstab_entry of $name is $fstab_entry"

  local dev
  if [ "$dynamic_partitions" = "true" ]; then
    if [ -n "$fstab_entry" ]; then
      dev="${BLK_PATH}/${fstab_entry}${SLOT_SUFFIX}"
    else
      dev="${BLK_PATH}/${name}${SLOT_SUFFIX}"
    fi
  else
    if [ -n "$fstab_entry" ]; then
      dev="${fstab_entry}${SLOT_SUFFIX}"
    else
      dev="${BLK_PATH}/${name}${SLOT_SUFFIX}"
    fi
  fi
  addToLog "- checking if $dev is block"
  if [ -b "$dev" ]; then
    addToLog "- Block Dev: $dev"
    echo "$dev"
  fi
}

find_gapps_size() {
  file_value=$(cat $COMMONDIR/file_size)
  for i in $file_value; do
    install_pkg_title=$(echo "$i" | cut -d'=' -f 1)
    install_pkg_size=$(echo "$i" | cut -d'=' -f 2)
    if [ -f "$nikgapps_config_file_name" ]; then
      value=$(ReadConfigValue ">>$install_pkg_title" "$nikgapps_config_file_name")
      [ -z "$value" ] && value=$(ReadConfigValue "$install_pkg_title" "$nikgapps_config_file_name")
      [ "$value" != "0" ] && value=1
    else
      abort "NikGapps Config not found!"
    fi
    if [ "$value" = "1" ]; then
      gapps_size=$((gapps_size+install_pkg_size))
    fi
  done
  test "$zip_type" != "debloater" && ui_print "- Gapps Size: $gapps_size KB"
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

find_system_size() {
  ui_print " "
  ui_print "--> Fetching system size"
  [ "$system_size" != "0" ] && ui_print "- /system available size: $system_size KB"
  [ "$product_size" != "0" ] && ui_print "- /product available size: $product_size KB"
  [ "$system_ext_size" != "0" ] && ui_print "- /system_ext available size: $system_ext_size KB"
  total_size=$((system_size+product_size+system_ext_size))
  addToLog "- Total available size: $total_size KB"
}

find_partition_type() {
  for partition in "system" "product" "system_ext"; do
    addToLog "----------------------------------------------------------------------------"
    addToLog "- Finding partition type for /$partition"
    mnt_point="/$partition"
    mountpoint "$mnt_point" >/dev/null 2>&1 && addToLog "- $mnt_point already mounted!"
    [ "$mnt_point" != "/system" ] && [ -L "$system$mnt_point" ] && addToLog "- $system$mnt_point symlinked!"
    blk_dev=$(find_block "$partition")
    if [ -n "$blk_dev" ]; then
      addToLog "- Found block for $mnt_point"
      case "$partition" in
        "system")
          system="/system"
          system_size=$(get_available_size "system")
          [ "$system_size" != "Used" ] && addToLog "- /system available size: $system_size KB"
          [ "$system_size" = "Used" ] && system_size=0
        ;;
        "product")
          product="/product"
          product_size=$(get_available_size "product")
          [ "$product_size" != "Used" ] && addToLog "- /product available size: $product_size KB"
          [ "$product_size" = "Used" ] && product_size=0
        ;;
        "system_ext")
          system_ext="/system_ext"
          system_ext_size=$(get_available_size "system_ext")
          [ "$system_ext_size" != "Used" ] && addToLog "- /system_ext available size: $system_ext_size KB"
          [ "$system_ext_size" = "Used" ] && system_ext_size=0
        ;;
      esac
      ui_print "- /$partition is mounted as dedicated partition"
    else
      case "$partition" in
        "system") system="/system" ;;
        "product") product="/system/product" ;;
        "system_ext") system_ext="/system/system_ext" ;;
      esac
      ui_print "- /$partition is symlinked to /system/$partition"
    fi
    case "$partition" in
        "system")
          is_system_writable="$(is_mounted_rw "$system" 2>/dev/null)"
          [ ! "$is_system_writable" ] && system=""
          addToLog "- system=$system is writable? $is_system_writable"
         ;;
        "product")
          is_product_writable="$(is_mounted_rw "$product" 2>/dev/null)"
          [ ! "$is_product_writable" ] && product=""
          addToLog "- product=$product is writable? $is_product_writable"
         ;;
        "system_ext")
          is_system_ext_writable="$(is_mounted_rw "$system_ext" 2>/dev/null)"
          [ ! "$is_system_ext_writable" ] && system_ext=""
          addToLog "- system_ext=$system_ext is writable? $is_system_ext_writable"
         ;;
      esac
  done
}

mount_system_source() {
  local system_source
  system_source=$(grep ' /system ' /etc/fstab | tail -n1 | cut -d' ' -f1)
  if [ -z "${system_source}" ]; then
    system_source=$(grep ' /system_root ' /etc/fstab | tail -n1 | cut -d' ' -f1)
  fi
  if [ -z "${system_source}" ]; then
    system_source=$(grep ' / ' /etc/fstab | tail -n1 | cut -d' ' -f1)
  fi
  addToLog "- system source is ${system_source}"
  addToLog "- fstab source is /etc/fstab"
  echo "${system_source}"
}

show_device_info() {
  ui_print " "
  ui_print "--> Fetching Device Information"
  mount_system_source
  sdkVersion=$(get_prop "ro.build.version.sdk")
  androidVersion=$(get_prop "ro.build.version.release")
  model=$(get_prop "ro.product.system.model")
  # Device details
  for field in ro.product.device ro.build.product ro.product.name ro.product.model; do
    device_name="$(get_prop "$field")"
    addToLog "- Field Name: $field"
    addToLog "- Device name: $device_name"
    if [ "${#device_name}" -ge "2" ]; then
      break
    fi
  done
  device=$(get_file_prop "$system/build.prop" "ro.product.system.device")
  if [ -z "$device" ]; then
    addToLog "- Device code not found!"
    device=$device_name
    if [ -z "$device" ]; then
      abort "NikGapps not supported for your device yet!"
    fi
  fi

  device_ab=$(getprop ro.build.ab_update 2>/dev/null)
  dynamic_partitions=$(getprop ro.boot.dynamic_partitions)
  [ -z "$dynamic_partitions" ] && dynamic_partitions="false"
  addToLog "- variable dynamic_partitions = $dynamic_partitions"
  BLK_PATH=/dev/block/bootdevice/by-name
  if [ -d /dev/block/mapper ]; then
    dynamic_partitions="true"
    BLK_PATH="/dev/block/mapper"
    addToLog "- Directory method! Device with dynamic partitions Found"
  else
    addToLog "- Device doesn't have dynamic partitions"
  fi

  SLOT=$(find_slot)
  if [ -n "$SLOT" ]; then
    if [ "$SLOT" = "_a" ]; then
      # Opposite slot
      SLOT_SUFFIX="_b"
    else
      SLOT_SUFFIX="_a"
    fi
  fi
  ui_print "- SDK Version: $sdkVersion"
  ui_print "- Android Version: $androidVersion"
  [ -n "$model" ] && ui_print "- Device: $model"
  [ -z "$model" ] && ui_print "- Device: $device"
  [ -z "$SLOT" ] || ui_print "- Current boot slot: $SLOT"
  if [ "$device_ab" = "true" ]; then
    ui_print "- A/B Device Found"
  else
    ui_print "- A-Only Device Found"
  fi
  addToLog "- Dynamic Partitions is $dynamic_partitions"
  if [ "$dynamic_partitions" = "true" ]; then
    ui_print "- Device has Dynamic Partitions"
  else
    addToLog "- Devices doesn't have Dynamic Partitions"
  fi
  addToLog "- Block Path = $BLK_PATH"
}