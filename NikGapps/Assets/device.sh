#!/sbin/sh

get_available_size() {
    df=$(df -k /"$1" | tail -n 1)
    case $df in
        /dev/block/*) df=$(echo "$df" | awk '{ print substr($0, index($0,$2)) }');;
    esac
    free_size_kb=$(echo "$df" | awk '{ print $3 }')
    size_of_partition=$(echo "$df" | awk '{ print $5 }')
    addToLog "- free_size_kb: $free_size_kb for $size_of_partition which should be $1"
    [ "$free_size_kb" = "Used" ] && free_size_kb=0
    echo "$free_size_kb"
}

get_block_for_mount_point() {
  grep -v "^#" /etc/recovery.fstab | grep " $1 " | tail -n1 | tr -s ' ' | cut -d' ' -f1
}

find_block() {
  local name="$1"
  local fstab_entry=$(get_block_for_mount_point "/$name")
  # P-SAR hacks
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/")
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/system_root")

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

find_device_block() {
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
      SLOT_SUFFIX="_a"
    else
      SLOT_SUFFIX="_b"
    fi
  fi
  addToLog "- Finding device block"
  SYSTEM_BLOCK=$(find_block "system")
  addToLog "- System_Block=$SYSTEM_BLOCK"
  PRODUCT_BLOCK=$(find_block "product")
  addToLog "- Product_Block=$PRODUCT_BLOCK"
  SYSTEM_EXT_BLOCK=$(find_block "system_ext")
  addToLog "- System_Ext_Block=$SYSTEM_EXT_BLOCK"
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
  ui_print "- Total available size: $total_size KB"
  [ "$total_size" = "0" ] && addToLog "No space left on device"
  [ "$total_size" = "0" ] && ui_print "- Unable to calculate space"
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