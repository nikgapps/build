#!/sbin/sh

begin_mounting() {
  $BOOTMODE && return 1;
  ui_print " "
  ui_print "--> Mounting partitions"
  mount_all;
  OLD_LD_PATH=$LD_LIBRARY_PATH;
  OLD_LD_PRE=$LD_PRELOAD;
  OLD_LD_CFG=$LD_CONFIG_FILE;
  unset LD_LIBRARY_PATH LD_PRELOAD LD_CONFIG_FILE;
  if [ ! "$(getprop 2>/dev/null)" ]; then
    getprop() {
      local propdir propfile propval;
      for propdir in / /system_root /system /vendor /product /system_ext /odm; do
        for propfile in default.prop build.prop; do
          test "$propval" && break 2 || propval="$(file_getprop $propdir/$propfile "$1" 2>/dev/null)";
        done;
      done;
      test "$propval" && echo "$propval" || echo "";
    }
  elif [ ! "$(getprop ro.build.type 2>/dev/null)" ]; then
    getprop() {
      ($(which getprop) | $BB grep "$1" | $BB cut -d[ -f3 | $BB cut -d] -f1) 2>/dev/null;
    }
  fi;
}

find_partition_type() {
  addToLog "----------------------------------------------------------------------------"
  addToLog "- Finding partition type for /system"
  blk_dev=$(find_block "system")
  if [ -n "$blk_dev" ]; then
      addToLog "- Found block for /system"
  fi
  system="/system"
  system_size=$(get_available_size "system")
  [ "$system_size" != "0" ] && addToLog "- /system available size: $system_size KB" && ui_print "- /system is mounted as dedicated partition"
  [ "$system_size" = "0" ] && system_size=0
  is_system_writable="$(is_mounted_rw "$system" 2>/dev/null)"
  [ ! "$is_system_writable" ] && system=""
  addToLog "- system=$system is writable? $is_system_writable"
  if [ -f "/system/build.prop" ]; then
    addToLog "- /system/build.prop exists"
  fi
  for partition in "product" "system_ext"; do
    addToLog "----------------------------------------------------------------------------"
    addToLog "- Finding partition type for /$partition"
    mnt_point="/$partition"
    already_mounted=false
    already_symlinked=false
    mountpoint "$mnt_point" >/dev/null 2>&1 && already_mounted=true && addToLog "- $mnt_point already mounted!"
    [ -L "$system$mnt_point" ] && already_symlinked=true && addToLog "- $system$mnt_point symlinked!"
    blk_dev=$(find_block "$partition")
    if [ "$already_mounted" = "false" ] || [ -z "$blk_dev" ] ||
     [ "$already_symlinked" = "true" ] || [ "$dynamic_partitions" = "false" ]; then
      case "$partition" in
        "product") product="$system/product" ;;
        "system_ext") system_ext="$system/system_ext" ;;
      esac
      ui_print "- /$partition is symlinked to $system/$partition"
    elif [ "$dynamic_partitions" = "true" ]; then
      if [ -n "$blk_dev" ]; then
        addToLog "- Found block for $mnt_point"
        case "$partition" in
          "product")
            product="/product"
            product_size=$(get_available_size "product")
            [ "$product_size" != "0" ] && addToLog "- /product available size: $product_size KB"
            [ "$product_size" = "0" ] && product_size=0
          ;;
          "system_ext")
            system_ext="/system_ext"
            system_ext_size=$(get_available_size "system_ext")
            [ "$system_ext_size" != "0" ] && addToLog "- /system_ext available size: $system_ext_size KB"
            [ "$system_ext_size" = "0" ] && system_ext_size=0
          ;;
        esac
        ui_print "- /$partition is mounted as dedicated partition"
      else
        addToLog "- /$partition block not found in dynamic_partitions device"
      fi
    fi
    case "$partition" in
      "product")
        is_product_writable="$(is_mounted_rw "$product" 2>/dev/null)"
        [ ! "$is_product_writable" ] && product=""
        addToLog "- product=$product is writable? $is_product_writable"
        if [ -f "/product/build.prop" ]; then
          addToLog "- /product/build.prop exists"
        elif [ -f "/system/product/build.prop" ]; then
          addToLog "- /system/product/build.prop exists"
        else
          addToLog "- product build.prop doesn't exists"
        fi
        ;;
      "system_ext")
        is_system_ext_writable="$(is_mounted_rw "$system_ext" 2>/dev/null)"
        [ ! "$is_system_ext_writable" ] && system_ext=""
        addToLog "- system_ext=$system_ext is writable? $is_system_ext_writable"
        if [ -f "/system_ext/build.prop" ]; then
          addToLog "- /system_ext/build.prop exists"
        elif [ -f "/system/system_ext/build.prop" ]; then
          addToLog "- /system/system_ext/build.prop exists"
        else
          addToLog "- system_ext build.prop doesn't exists"
        fi
        ;;
    esac
  done
}

is_mounted_rw() {
  local mounted_rw=false
  local startswith=$(beginswith / "$1")
  test "$startswith" == "false" && part=/"$1" || part="$1"
  touch "$part"/.rw && rm "$part"/.rw && mounted_rw=true
  addToLog "- checked if $part/.rw is writable i.e. $mounted_rw ($1/.rw being original argument)"
  echo $mounted_rw
}

# Mount all the partitions
mount_all() {
  local byname mount slot system;
  if ! is_mounted /cache; then
    mount /cache 2>/dev/null && UMOUNT_CACHE=1
  fi
  if ! is_mounted /data; then
    ui_print "- Mounting /data"
    $BB mount /data && UMOUNT_DATA=1
  else
    addToLog "- /data already mounted!"
  fi;

  (for mount in /vendor /product /system_ext /persist; do
    ui_print "- Mounting $mount"
    $BB mount -o ro -t auto $mount;
  done) 2>/dev/null;

  addToLog "----------------------------------------------------------------------------"
  ui_print "- Mounting $ANDROID_ROOT"
  addToLog "- Setting up mount point $ANDROID_ROOT"
  addToLog "- ANDROID_ROOT=$ANDROID_ROOT"
  setup_mountpoint "$ANDROID_ROOT"
  if ! is_mounted "$ANDROID_ROOT"; then
    mount -o ro -t auto "$ANDROID_ROOT" 2>/dev/null
  fi
  addToLog "----------------------------------------------------------------------------"
  byname=bootdevice/by-name;
  [ -d /dev/block/$byname ] || byname=$($BB find /dev/block/platform -type d -name by-name 2>/dev/null | $BB head -n1 | $BB cut -d/ -f4-);
  [ -d /dev/block/mapper ] && byname=mapper && addToLog "- Device with dynamic partitions Found";
  [ -e /dev/block/$byname/system ] || slot=$(find_slot);
  case $ANDROID_ROOT in
    /system_root) setup_mountpoint /system;;
    /system)
      if ! is_mounted /system && ! is_mounted /system_root; then
        setup_mountpoint /system_root;
        addToLog "- mounting /system_root partition as readwrite"
        $BB mount -o rw -t auto /system_root;
      elif [ -f /system/system/build.prop ]; then
        setup_mountpoint /system_root;
        addToLog "- Moving /system to /system_root"
        $BB mount --move /system /system_root;
      fi;
      ret=$?
      addToLog "- Command Execution Status: $ret"
      if [ $ret -ne 0 ]; then
        addToLog "- Unmounting and Remounting /system as /system_root"
        ($BB umount /system;
        $BB umount -l /system) 2>/dev/null
        $BB mount -o ro -t auto /dev/block/$byname/system$slot /system_root;
      else
         addToLog "- $ret should be equals to 0"
      fi
    ;;
  esac;
  [ -f /system_root/system/build.prop ] && system=/system;
  for mount in /vendor /product /system_ext; do
      if ! is_mounted $mount && [ -L /system$mount -o -L /system_root$system$mount ]; then
        setup_mountpoint $mount;
        $BB mount -o ro -t auto /dev/block/$byname$mount$slot $mount;
      fi;
  done;
  addToLog "----------------------------------------------------------------------------"
  addToLog "- Checking if /system_root is mounted.."
  addToLog "----------------------------------------------------------------------------"
  if is_mounted /system_root; then
    mount_apex;
    $BB mount -o bind /system_root$system /system;
  elif is_mounted /system; then
    addToLog "- /system is mounted"
  else
    addToLog "- Could not mount /system"
    abort "- Could not mount /system, try changing recovery!"
  fi;
  if ! is_mounted /persist && [ -e /dev/block/bootdevice/by-name/persist ]; then
    setup_mountpoint /persist;
    $BB mount -o ro -t auto /dev/block/bootdevice/by-name/persist /persist;
  fi;
  addToLog "----------------------------------------------------------------------------"
  system=/system
  if [ -d /dev/block/mapper ]; then
    for block in system vendor product system_ext; do
      for slot in "" _a _b; do
        addToLog "- Executing blockdev setrw /dev/block/mapper/$block$slot"
        blockdev --setrw /dev/block/mapper/$block$slot 2>/dev/null
      done
    done
  addToLog "----------------------------------------------------------------------------"
  fi
  mount -o rw,remount -t auto /system || mount -o rw,remount -t auto /
  for partition in "vendor" "product" "system_ext"; do
    addToLog "- Remounting /$partition as read write"
    mount -o rw,remount -t auto "/$partition" 2>/dev/null
  done
  if [ -n "$PRODUCT_BLOCK" ]; then
    if ! is_mounted /product; then
      mkdir /product || true
      if mount -o rw "$PRODUCT_BLOCK" /product; then
        addToLog "- /product mounted"
      else
        addToLog "- Could not mount /product"
      fi
    else
      addToLog "- /product already mounted"
    fi
  fi
  if [ -n "$SYSTEM_EXT_BLOCK" ]; then
    if ! is_mounted /system_ext; then
      mkdir /system_ext || true
      if mount -o rw "$SYSTEM_EXT_BLOCK" /system_ext; then
        addToLog "- /system_ext mounted"
      else
        addToLog "- Could not mount /system_ext"
      fi
    else
      addToLog "- /system_ext already mounted"
    fi
  fi
  addToLog "----------------------------------------------------------------------------"
  ls -alR /system > "$COMMONDIR/System_Files_Before.txt"
  ls -alR /product > "$COMMONDIR/Product_Files_Before.txt"
  df > "$COMMONDIR/size_before.txt"
  df -h > "$COMMONDIR/readable_size_before.txt"
  copy_file "$COMMONDIR/size_before.txt" "$logDir/partitions/size_before.txt"
  copy_file "$COMMONDIR/readable_size_before.txt" "$logDir/partitions/readable_size_before.txt"
  # find if the device has dedicated partition or it's symlinked
  find_partition_type
}

# More info on Apex here -> https://www.xda-developers.com/android-q-apex-biggest-tdynamic_partitionshing-since-project-treble/
mount_apex() {
  [ -d /system_root/system/apex ] || return 1;
  local apex dest loop minorx num var;
  setup_mountpoint /apex;
  minorx=1;
  [ -e /dev/block/loop1 ] && minorx=$($BB ls -l /dev/block/loop1 | $BB awk '{ print $6 }');
  num=0;
  for apex in /system_root/system/apex/*; do
    dest=/apex/$($BB basename $apex .apex);
    case $dest in
      *.current|*.release) dest=$(echo $dest | $BB rev | $BB cut -d. -f2- | $BB rev);;
    esac;
    $BB mkdir -p $dest;
    case $apex in
      *.apex)
        $BB unzip -qo $apex apex_payload.img -d /apex;
        $BB mv -f /apex/apex_payload.img $dest.img;
        $BB mount -t ext4 -o ro,noatime $dest.img $dest 2>/dev/null;
        if [ $? != 0 ]; then
          while [ $num -lt 64 ]; do
            loop=/dev/block/loop$num;
            ($BB mknod $loop b 7 $((num * minorx));
            $BB losetup $loop $dest.img) 2>/dev/null;
            num=$((num + 1));
            $BB losetup $loop | $BB grep -q $dest.img && break;
          done;
          $BB mount -t ext4 -o ro,loop,noatime $loop $dest;
          if [ $? != 0 ]; then
            $BB losetup -d $loop 2>/dev/null;
          fi;
        fi;
      ;;
      *) $BB mount -o bind $apex $dest;;
    esac;
  done;
  for var in $($BB grep -o 'export .* /.*' /system_root/init.environ.rc | $BB awk '{ print $2 }'); do
    eval OLD_${var}=\$$var;
  done;
  $($BB grep -o 'export .* /.*' /system_root/init.environ.rc | $BB sed 's; /;=/;'); unset export;
}
