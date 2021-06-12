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
      for propdir in / /system_root /system /vendor /odm /product; do
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
  find_device_block
  # Check A/B slot
  [ -z "$SLOT" ] || ui_print "- Current boot slot: $SLOT"
  if ! is_mounted /cache; then
    mount /cache 2>/dev/null && UMOUNT_CACHE=1
  fi
  if ! is_mounted /data; then
    ui_print "- Mounting /data"
    $BB mount /data && UMOUNT_DATA=1
  else
    addToLog "- /data already mounted!"
  fi;

  (for partition in "vendor" "product" "persist"; do
    ui_print "- Mounting /$partition"
    $BB mount -o ro -t auto "/$partition" 2>/dev/null;
  done) 2>/dev/null
  addToLog "----------------------------------------------------------------------------"
  ui_print "- Mounting $ANDROID_ROOT"
  addToLog "- Setting up mount point $ANDROID_ROOT"
  addToLog "- ANDROID_ROOT=$ANDROID_ROOT"
  setup_mountpoint "$ANDROID_ROOT"
  if ! is_mounted "$ANDROID_ROOT"; then
    mount -o ro -t auto "$ANDROID_ROOT" 2>/dev/null
  fi
  addToLog "----------------------------------------------------------------------------"
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
        (umount /system;
        umount -l /system) 2>/dev/null
        if [ -d /dev/block/mapper ]; then
          addToLog "- Device with dynamic partitions Found"
          test -e /dev/block/mapper/system || local slot=$(find_slot)
          addToLog "- Mounting /system$slot as read only"
          mount -o ro -t auto /dev/block/mapper/system"$slot" /system_root
          for partition in "vendor" "product" "system_ext"; do
            addToLog "- Mounting /$partition$slot as read only"
            mount -o ro -t auto /dev/block/mapper/$partition"$slot" /partition 2>/dev/null
          done
        else
          test -e /dev/block/bootdevice/by-name/system || local slot=$(find_slot)
          addToLog "- Device doesn't have dynamic partitions, mounting /system$slot as ro"
          mount -o ro -t auto /dev/block/bootdevice/by-name/system"$slot" /system_root
          (for partition in "vendor" "product" "persist system_ext"; do
            ui_print "- Mounting /$partition as read only"
            mount -o ro -t auto /dev/block/bootdevice/by-name/"$partition$slot" /"$partition"
          done) 2>/dev/null
        fi
      else
         addToLog "- $ret should be equals to 0"
      fi
    ;;
  esac;
  addToLog "----------------------------------------------------------------------------"
  addToLog "- Checking if /system_root is mounted.."
  addToLog "----------------------------------------------------------------------------"
  if is_mounted /system_root; then
    mount_apex;
    if [ -f /system_root/build.prop ]; then
      addToLog "- Binding /system_root as /system"
      $BB mount -o bind /system_root /system;
    else
      addToLog "- Binding /system_root/system as /system"
      $BB mount -o bind /system_root/system /system;
    fi;
  elif is_mounted /system; then
    addToLog "- /system is mounted"
  else
    addToLog "- Could not mount /system"
    abort "- Could not mount /system, try changing recovery!"
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
  addToLog "----------------------------------------------------------------------------"
  if [ -n "$PRODUCT_BLOCK" ]; then
    mkdir /product || true
    if mount -o rw "$PRODUCT_BLOCK" /product; then
      addToLog "- /product mounted"
    else
      addToLog "- Could not mount /product"
    fi
  fi
  if [ -n "$SYSTEM_EXT_BLOCK" ]; then
    mkdir /system_ext || true
    if mount -o rw "$SYSTEM_EXT_BLOCK" /system_ext; then
      addToLog "- /system_ext mounted"
    else
      addToLog "- Could not mount /system_ext"
    fi
  fi
  ls -alR /system > "$COMMONDIR/System_Files_Before.txt"
  ls -alR /product > "$COMMONDIR/Product_Files_Before.txt"
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
