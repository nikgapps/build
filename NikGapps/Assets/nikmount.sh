#!/sbin/sh

get_available_size() {
    df=$(df -k /"$1" | tail -n 1)
    case $df in
        /dev/block/*) df=$(echo "$df" | awk '{ print substr($0, index($0,$2)) }');;
    esac
    free_system_size_kb=$(echo "$df" | awk '{ print $3 }')
    echo "$free_system_size_kb"
}

find_system_size() {
  ui_print " "
  ui_print "--> Fetching system size"
  system_size=$(get_available_size "system")
  [ "$system_size" != "Used" ] && ui_print "- /system available size: $system_size KB"
  [ "$system_size" = "Used" ] && system_size=0

  product_size=$(get_available_size "product")
  [ "$product_size" != "Used" ] && ui_print "- /product available size: $product_size KB"
  [ "$product_size" = "Used" ] && product_size=0

  system_ext_size=$(get_available_size "system_ext")
  [ "$system_ext_size" != "Used" ] && ui_print "- /system_ext available size: $system_ext_size KB"
  [ "$system_ext_size" = "Used" ] && system_ext_size=0

  total_size=$((system_size+product_size+system_ext_size))

  addToLog "- Total available size: $total_size KB"
}

get_block_for_mount_point() {
  grep -v "^#" /vendor/etc/fstab.$(getprop ro.boot.hardware) | grep " $1 " | tail -n1 | tr -s ' ' | cut -d' ' -f1
}

find_partition_type() {
  for partition in "product" "system_ext"; do
    addToLog "- Finding partition type for /$partition"
    mnt_point="/$partition"
    mountpoint "$mnt_point" >/dev/null 2>&1 && addToLog "- $mnt_point already mounted!"
    [ -L "$mnt_point" ] && addToLog "- $mnt_point symlinked!"
    blk_dev=$(find_my_block "$partition")
    if [ -n "$blk_dev" ]; then
      addToLog "- Found block for $mnt_point"
      case "$partition" in
        "product") product="/product" ;;
        "system_ext") system_ext="/system_ext" ;;
      esac
      ui_print "- /$partition is mounted as dedicated partition"
    else
      case "$partition" in
        "product") product="/system/product" ;;
        "system_ext") system_ext="/system/system_ext" ;;
      esac
      ui_print "- /$partition is symlinked to /system/$partition"
    fi
  done
}

find_my_block() {
  local name="$1"
  local fstab_entry=$(get_block_for_mount_point "/$name")
  # P-SAR hacks
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/")
  [ -z "$fstab_entry" ] && [ "$name" = "system" ] && fstab_entry=$(get_block_for_mount_point "/system_root")

  local dev
  if [ "$DYNAMIC_PARTITIONS" = "true" ]; then
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
  if [ -b "$dev" ]; then
    addToLog "Block Dev: $dev"
    echo "$dev"
  fi
}

# Unmount all partitions on recovery clean up and for a fresh install
umount_all() {
  (if [ ! -d /postinstall/tmp ]; then
    ui_print "- Unmounting /system"
    $BB umount /system;
    $BB umount -l /system;
    $BB umount /mnt/system
    $BB umount -l /mnt/system
    umount_apex;
    if [ -e /system_root ]; then
      ui_print "- Unmounting /system_root"
      $BB umount /system_root;
      $BB umount -l /system_root;
    fi;
    $BB umount /mnt/system;
    $BB umount -l /mnt/system;
  fi;
  ui_print "- Unmounting /vendor"
  $BB umount /vendor;
  $BB umount -l /vendor;
  $BB umount /mnt/vendor;
  $BB umount -l /mnt/vendor;
  addToLog "- Unmounting /persist"
  $BB umount /persist
  $BB umount -l /persist
  ui_print "- Unmounting /product"
  $BB umount /product;
  $BB umount -l /product;
  $BB umount /mnt/product
  $BB umount -l /mnt/product
  if [ "$UMOUNT_DATA" ]; then
    ui_print "- Unmounting /data"
    $BB umount /data;
    $BB umount -l /data;
  fi
  if [ "$UMOUNT_CACHE" ]; then
    $BB umount /cache
    $BB umount -l /cache
  fi) 2>/dev/null;
}

begin_unmounting() {
  $BOOTMODE && return 1;
  $BB mount -o bind /dev/urandom /dev/random;
  if [ -L /etc ]; then
    setup_mountpoint /etc;
    $BB cp -af /etc_link/* /etc;
    $BB sed -i 's; / ; /system_root ;' /etc/fstab;
  fi;
  ui_print " "
  ui_print "--> Unmounting partitions for fresh install"
  umount_all;
}

begin_unmounting