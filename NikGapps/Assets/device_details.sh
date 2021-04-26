#!/sbin/sh

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

mount_system_source

dynamic_partitions=$(getprop ro.boot.dynamic_partitions)
[ -z "$dynamic_partitions" ] && dynamic_partitions="false"
addToLog "- Dynamic Partitions is $dynamic_partitions"

device_ab=$(getprop ro.build.ab_update 2>/dev/null)

BLK_PATH=/dev/block/bootdevice/by-name
[ "$dynamic_partitions" = "true" ] && BLK_PATH="/dev/block/mapper"
addToLog "- Block Path = $BLK_PATH"

SLOT=$(find_slot)
if [ -n "$SLOT" ]; then
  if [ "$SLOT" = "_a" ]; then
    # Opposite slot
    SLOT_SUFFIX="_b"
  else
    SLOT_SUFFIX="_a"
  fi
fi