#!/sbin/sh

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

# Unmount apex partition upon recovery cleanup
umount_apex() {
  [ -d /apex/com.android.runtime ] || return 1;
  local dest loop var;
  for var in $($BB grep -o 'export .* /.*' /system_root/init.environ.rc | $BB awk '{ print $2 }'); do
    if [ "$(eval echo \$OLD_$var)" ]; then
      eval $var=\$OLD_${var};
    else
      eval unset $var;
    fi;
    unset OLD_${var};
  done;
  for dest in $($BB find /apex -type d -mindepth 1 -maxdepth 1); do
    if [ -f $dest.img ]; then
      loop=$($BB mount | $BB grep $dest | $BB cut -d\  -f1);
    fi;
    ($BB umount -l $dest;
    $BB losetup -d $loop) 2>/dev/null;
  done;
  $BB rm -rf /apex 2>/dev/null;
}
