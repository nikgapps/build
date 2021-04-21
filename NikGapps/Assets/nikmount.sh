#!/sbin/sh

lets_mount() {
  export all_V3_partitions="system vendor product system_ext"
  mount_extra $all_V3_partitions
}

get_block_for_mount_point() {
  grep -v "^#" /vendor/etc/fstab.$(getprop ro.boot.hardware) | grep " $1 " | tail -n1 | tr -s ' ' | cut -d' ' -f1
}

mount_extra() {
  for partition in "$@"; do
    ui_print "mounting extra for $partition"
    mnt_point="/$partition"
    mountpoint "$mnt_point" >/dev/null 2>&1 && ui_print "already mounted!" && continue
    [ -L "$mnt_point" ] && ui_print "symlinked!" && continue

    blk_dev=$(find_my_block "$partition")
    if [ -n "$blk_dev" ]; then
      [ "$DYNAMIC_PARTITIONS" = "true" ] && blockdev --setrw "$blk_dev"
#      mount -o rw "$blk_dev" "$mnt_point"
      ui_print "Mounting ro"
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
    ui_print "Block Dev: $dev"
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