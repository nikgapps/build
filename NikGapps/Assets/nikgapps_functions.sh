#!/sbin/sh

abort() {
  ui_print " "
  ui_print "----------------------------------------------------"
  ui_print "$@"
  ui_print "----------------------------------------------------"
  ui_print " "
  exit_install
  exit 1
}

beginswith() {
  case $2 in
    "$1"*) echo true ;;
    *) echo false ;;
  esac
}

# this is how we can use calc_progress
# index=1
# count=10
# for i in $package_list; do
#     temp_value=$(calc_progress $index/$count)
#     addToLog "- Progress Value=$temp_value"
#     index=`expr $index + 1`
# done
calc_progress() { awk "BEGIN{print $*}" | awk '{print sprintf("%.2f", $1)}'; }

calculate_space_after(){
  addToLog "----------------------------------------------------------------------------" "$1"
  addToLog "- calculating space after installing $1" "$1"
  size_before=$3
  pkg_size=$4
  case "$2" in
    "/product") size_left=$(get_available_size_again "/product");
      addToLog "- product_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
      addSizeToLog "/product" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
    ;;
    "/system_ext") size_left=$(get_available_size_again "/system_ext");
      addToLog "- system_ext_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
      addSizeToLog "/system_ext" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
    ;;
    "/system") size_left=$(get_available_size_again "/system");
      addToLog "- system_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
      addSizeToLog "/system" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
    ;;
    "/system/product")
      if [ -n "$PRODUCT_BLOCK" ]; then
        size_left=$(get_available_size_again "/product");
        addToLog "- product_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
        addSizeToLog "/product" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
      else
        size_left=$(get_available_size_again "/system");
        addToLog "- system_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
        addSizeToLog "/system" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
      fi
    ;;
    "/system/system_ext")
      if [ -n "$SYSTEM_EXT_BLOCK" ]; then
        size_left=$(get_available_size_again "/system_ext");
        addToLog "- system_ext_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
        addSizeToLog "/system_ext" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
      else
        size_left=$(get_available_size_again "/system");
        addToLog "- system_size ($size_before-$size_left) spent=$((size_before-size_left)) vs ($pkg_size)" "$1";
        addSizeToLog "/system" "$2" "$1" "$size_before" "$size_left" "$pkg_size" "$((size_before-size_left))"
      fi
    ;;
  esac
  addToLog "----------------------------------------------------------------------------" "$1"
  [ -z "$size_left" ] && size_left=0
  echo "$size_left"
}

calculate_space_before() {
  dir=$2
  addToLog "----------------------------------------------------------------------------" "$1"
  addToLog "- calculating space before installing $1" "$1"
  size_left=0
  case "$dir" in
    "/product")
      size_left=$(get_available_size_again "$dir" "$1") ;;
    "/system_ext")
      size_left=$(get_available_size_again "$dir" "$1") ;;
    "/system")
      size_left=$(get_available_size_again "$dir" "$1") ;;
    "/system/product")
      if [ -n "$PRODUCT_BLOCK" ]; then
        size_left=$(get_available_size_again "/product" "$1")
      else
        size_left=$(get_available_size_again "/system" "$1")
      fi ;;
    "/system/system_ext")
      if [ -n "$SYSTEM_EXT_BLOCK" ]; then
        size_left=$(get_available_size_again "/system_ext" "$1")
      else
        size_left=$(get_available_size_again "/system" "$1")
      fi ;;
  esac
  addToLog "- ${dir} size left=$size_left" "$1"
  addToLog "----------------------------------------------------------------------------" "$1"
  echo "$size_left"
}

calculate_space() {
  local partitions="$*"
  for partition in $partitions; do
    addToLog " "
    if ! is_mounted "/$partition"; then
      continue
    fi
    addToLog "--> Calculating space in /$partition"
    # Read and save system partition size details
    df=$(df -k /"$partition" | tail -n 1)
    addToLog "$df"
    case $df in
    /dev/block/*) df=$(echo "$df" | $BB awk '{ print substr($0, index($0,$2)) }') ;;
    esac
    total_system_size_kb=$(echo "$df" | $BB awk '{ print $1 }')
    used_system_size_kb=$(echo "$df" | $BB awk '{ print $2 }')
    free_system_size_kb=$(echo "$df" | $BB awk '{ print $3 }')
    addToLog "- Total System Size (KB) $total_system_size_kb"
    addToLog "- Used System Space (KB) $used_system_size_kb"
    addToLog "- Current Free Space (KB) $free_system_size_kb"
    size_fetched_again=$(get_available_size_again "/$partition")
  done
}

ch_con() {
  chcon -h u:object_r:"${1}"_file:s0 "$2"
}

check_if_partitions_are_mounted_rw() {
  addToLog "- Bootmode: $BOOTMODE"
  $BOOTMODE and return
  addToLog "- Android version: $androidVersion"
  case "$androidVersion" in
    "10")
      system_ext="$product";
      [ ! "$is_system_writable" ] && [ ! "$is_product_writable" ] && abort "- Partitions not writable!"
    ;;
    "1"*)
      [ ! "$is_system_writable" ] && [ ! "$is_product_writable" ] && [ ! "$is_system_ext_writable" ] && abort "- Partitions not writable!"
    ;;
    *)
      product=""; system_ext="";
      [ ! "$is_system_writable" ] && abort "- Partitions not writable!"
    ;;
  esac
}

check_if_system_mounted_rw() {
  is_partition_mounted_flag="false"
  for partition in "system" "product" "system_ext"; do
    is_partition_mounted="$(is_mounted_rw "$partition" 2>/dev/null)"
    if [ "$is_partition_mounted" = "true" ]; then
      ui_print "- /$partition is properly mounted as rw"
      is_partition_mounted_flag="true"
    else
      addToLog "----------------------------------------------------------------------------"
      addToLog "- $partition is not mounted as rw, Installation failed!"
      addToLog "----------------------------------------------------------------------------"
    fi
  done
  [ "$is_partition_mounted_flag" = "false" ] && abort "- System is not mounted as rw, Installation failed!"
}

clean_recursive() {
  folders_that_exists=""
  func_result="$(beginswith / "$1")"
  addToLog "- Deleting $1 with func_result: $func_result" "$2"
  if [ "$func_result" = "true" ]; then
    if [ -e "$1" ]; then
       rm -rf "$1"
      folders_that_exists="$folders_that_exists":"$1"
    fi
  else
    for i in $(find "$system" "$product" "$system_ext" "/product" "/system_ext" -iname "$1" 2>/dev/null;); do
      addToLog "- Found $i" "$2"
      if [ -d "$i" ]; then
        addToLog "- Deleting $1" "$2"
        rm -rf "$i"
        folders_that_exists="$folders_that_exists":"$i"
      fi
    done
    # some devices fail to find the folder using above method even when the folder exists
    if [ -z "$folders_that_exists" ]; then
      for sys in "/system" "" "/system_root"; do
        for subsys in "/system" "/product" "/system_ext"; do
          for folder in "/app" "/priv-app"; do
            if [ -d "$sys$subsys$folder/$1" ] && [ "$sys$subsys$folder/" != "$sys$subsys$folder/$1" ]; then
              addToLog "- Hardcoded and Deleting $sys$subsys$folder/$1" "$2"
              rm -rf "$sys$subsys$folder/$1"
              folders_that_exists="$folders_that_exists":"$sys$subsys$folder/$1"
            fi
          done
        done
      done
    else
      addToLog "- search finished, $folders_that_exists deleted" "$2"
    fi
  fi
  echo "$folders_that_exists"
}

# This is meant to copy the files safely from source to destination
copy_file() {
  if [ -f "$1" ]; then
    mkdir -p "$(dirname "$2")"
    cp -f "$1" "$2"
  else
    addToLog "- File $1 does not exist!"
  fi
}

contains() {
  case $2 in
    *"$1"*) echo true ;;
    *) echo false ;;
  esac
}

get_prop_file_path() {
  propFilePath=""
  for i in $(find /system/etc/permissions -iname "$1.prop" 2>/dev/null;); do
    prop_file_path="$i"
    addToLog "- Found prop file: $prop_file_path" "$1"
    break
  done
  addToLog "- Prop file path before: $prop_file_path" "$1"
  [ -z "$prop_file_path" ] && prop_file_path="/system/etc/permissions/$1.prop"
  addToLog "- Prop file path after: $prop_file_path" "$1"
  echo "$prop_file_path"
}

get_available_size_again() {
  input_data=$1
  log_file_name=$2
  case $1 in
    "/"*) addToLog "- fetching size for $1" "$log_file_name" ;;
    *) input_data="/$1" ;;
  esac
  tmp_file=$COMMONDIR/available.txt
  available_size=""
  if ! is_mounted "$1"; then
    addToLog "- $1 not mounted!" "$log_file_name"
  else
    df | grep -vE '^Filesystem|tmpfs|cdrom' | while read output;
    do
      mounted_on=$(echo $output | $BB awk '{ print $5 }' )
      available_size=$(echo $output | $BB awk '{ print $3 }' )
      case $mounted_on in
        *"%"*)
        mounted_on=$(echo $output | $BB awk '{ print $6 }' )
        available_size=$(echo $output | $BB awk '{ print $4 }' )
        ;;
      esac
      if [ "$mounted_on" = "$1" ] || ([ "/system" = "$input_data" ] && [ "$mounted_on" = "/system_root" ]); then
        addToLog "- $input_data($mounted_on) available size: $available_size KB" "$log_file_name"
        echo $available_size > $tmp_file
        break
      fi
    done
  fi
  [ -f $tmp_file ] && available_size=$(cat $tmp_file)
  rm -rf $tmp_file
  [ -z $available_size ] && available_size=0
  echo $available_size
}

get_total_size_required() {
  total_size_required=0
  for i in $1; do
    package_size=$(echo "$i" | cut -d',' -f2)
    total_size_required=$((total_size_required + package_size))
  done
  echo $total_size_required
}

copy_file_logs() {
  mkdir -p "$logDir/partitions/$1"
  find /product /system /system_ext | sort >>"$logDir/partitions/$1/all_files.txt"
}

copy_logs() {
  copy_file "$system/build.prop" "$logDir/propfiles/build.prop"
  # Store the size of partitions after installation starts
  df >"$COMMONDIR/size_after.txt"
  df -h >"$COMMONDIR/size_after_readable.txt"
  copy_file "/vendor/etc/fstab.qcom" "$logDir/fstab/fstab.qcom"
  copy_file "/etc/recovery.fstab" "$logDir/fstab/recovery.fstab"
  copy_file "/etc/fstab" "$logDir/fstab/fstab"
  copy_file "$COMMONDIR/size_after.txt" "$logDir/partitions/size_after.txt"
  copy_file "$COMMONDIR/size_after_readable.txt" "$logDir/partitions/size_after_readable.txt"
  copy_file_logs "after"
  for f in $(find /system -iname "*.prop" 2>/dev/null); do
    copy_file "$f" "$logDir/propfiles/$f"
  done
  for f in $(find /product -iname "*.prop" 2>/dev/null); do
    copy_file "$f" "$logDir/propfiles/$f"
  done
  for f in $(find /system_ext -iname "*.prop" 2>/dev/null); do
    copy_file "$f" "$logDir/propfiles/$f"
  done
  for f in $addon_scripts_logDir; do
    copy_file "$f" "$logDir/addonscripts/$f"
  done
  calculate_space "system" "product" "system_ext"
  addToLog "- copying $debloater_config_file_name to log directory"
  copy_file "$debloater_config_file_name" "$logDir/configfiles/debloater.config"
  addToLog "- copying $nikgapps_config_file_name to log directory"
  copy_file "$nikgapps_config_file_name" "$logDir/configfiles/nikgapps.config"
  copy_file "$recoveryLog" "$logfilesDir/Recovery.log"
  addToLog "- Start Time: $start_time"
  addToLog "- End Time: $(date +%Y_%m_%d_%H_%M_%S)"
  copy_file "$nikGappsLog" "$logfilesDir/NikGapps.log"
  copy_file "$mountLog" "$logfilesDir/Mount.log"
  copy_file "$busyboxLog" "$logfilesDir/Busybox.log"
  copy_file "$installation_size_log" "$logfilesDir/Size.log"
  cd "$logDir" || return
  rm -rf "$nikGappsDir/logs"
  tar -cz -f "$TMPDIR/$nikGappsLogFile" *
  [ -z "$nikgapps_config_dir" ] && nikgapps_config_dir=/sdcard/NikGapps

  # if /userdata is encrypted, installer will copy the logs to system
  backup_logs_dir="$system/etc"
  OLD_IFS="$IFS"
  config_dir_list="$nikGappsDir:$nikgapps_config_dir:$nikgapps_log_dir:$backup_logs_dir"
  IFS=":"
  for dir in $config_dir_list; do
    if [ -d "$dir" ]; then
      archive_dir="$dir/nikgapps_logs_archive"
      mkdir -p "$archive_dir"
      mkdir -p "$dir/nikgapps_logs"
      mv "$dir/nikgapps_logs"/* "$archive_dir"
      copy_file "$TMPDIR/$nikGappsLogFile" "$dir/nikgapps_logs/$nikGappsLogFile"
    else
      ui_print "- $dir/nikgapps_logs not a directory"
    fi
  done
  IFS="$OLD_IFS"

  if [ -f "$nikgapps_log_dir/$nikGappsLogFile" ]; then
    ui_print "- Copying Logs at $nikgapps_log_dir/$nikGappsLogFile"
  elif [ -f "$nikgapps_config_dir/nikgapps_logs/$nikGappsLogFile" ]; then
    ui_print "- Copying Logs at $nikgapps_config_dir/nikgapps_logs/$nikGappsLogFile"
  elif [ -f "$nikGappsDir/nikgapps_logs/$nikGappsLogFile" ]; then
    ui_print "- Copying Logs at $nikGappsDir/nikgapps_logs/$nikGappsLogFile"
  else
    if [ -f "$backup_logs_dir/nikgapps_logs/$nikGappsLogFile" ]; then
      ui_print "- Copying Logs at $backup_logs_dir/nikgapps_logs/$nikGappsLogFile"
    else
      ui_print "- Couldn't copy logs, something went wrong!"
    fi
  fi
  
  ui_print " "
  cd /
}

debloat() {
  debloaterFilesPath="Debloater"
  propFilePath=$(get_prop_file_path $debloaterFilesPath)
  debloaterRan=0
  addon_index="04"
  if [ -f "$debloater_config_file_name" ]; then
    addToLog "- Debloater.config found!"
    g=$(sed -e '/^[[:blank:]]*#/d;s/[\t\n\r ]//g;/^$/d' "$debloater_config_file_name")
    for i in $g; do
      if [ $debloaterRan = 0 ]; then
        ui_print " "
        ui_print "--> Starting the debloating process"
      fi
      addToLog "- Deleting $i"
      if [ -z "$i" ]; then
        ui_print "Cannot delete blank folder!"
      else
        debloaterRan=1
        startswith=$(beginswith / "$i")
        if [ "$startswith" = "false" ]; then
          addToLog "- value of i is $i"
          debloated_folders=$(clean_recursive "$i" "$debloaterFilesPath")
          if [ -n "$debloated_folders" ]; then
            addToLog "- Removed folders: $debloated_folders"
            OLD_IFS="$IFS"
            IFS=":"
            for j in $debloated_folders; do
              if [ -n "$j" ]; then
                ui_print "x Removing $j"
                update_prop "$j" "debloat" "$propFilePath" "$debloaterFilesPath"
              fi
            done
            IFS="$OLD_IFS"
          else
            addToLog "- No $i folders to debloat"
            match=$(find_prop_match "$1" "debloat" "$3")
            if [ -z "$match" ]; then
              ui_print "x Removing $i"
              update_prop "$i" "forceDebloat" "$propFilePath" "$debloaterFilesPath"
            else
              ui_print "- $i already Debloated"
            fi
          fi
        else
          addToLog "- Force Removing $i"
          rm -rf "$i"
          match=$(find_prop_match "$1" "debloat" "$3")
          if [ -z "$match" ]; then
            ui_print "x Removing $i"
            update_prop "$i" "forceDebloat" "$propFilePath" "$debloaterFilesPath"
          else
            ui_print "- $i already Debloated"
          fi
        fi
      fi
    done
    if [ $debloaterRan = 1 ]; then
      update_prop "$propFilePath" "install" "$propFilePath" "$debloaterFilesPath"
      . $COMMONDIR/addon "Debloater" "$propFilePath" "$addon_index"
      copy_file "$system/addon.d/$addon_index-Debloater.sh" "$logDir/addonscripts/$addon_index-Debloater.sh"
    fi
  else
    addToLog "- Debloater.config not found!"
    unpack "afzc/debloater.config" "/sdcard/NikGapps/debloater.config"
  fi
  if [ $debloaterRan = 1 ]; then
    ui_print " "
  fi
}

delete_package() {
  deleted_folders=$(clean_recursive "$1" "$2")
  addToLog "- Deleted $deleted_folders as part of package $1" "$2"
}

delete_package_data() {
  addToLog "- Deleting data of package $1"
  rm -rf "/data/data/${1}*"
}

delete_recursive() {
  rm -rf "$*"
}

extract_file() {
  mkdir -p "$(dirname "$3")"
  addToLog "- Unzipping $1"
  addToLog "  -> copying $2"
  addToLog "  -> to $3"
  $BB unzip -o "$1" "$2" -p >"$3"
}

extract_pkg() {
  mkdir -p "$(dirname "$3")"
  addToLog "- Unzipping $1" "$4"
  addToLog "  -> copying $2" "$4"
  addToLog "  -> to $3" "$4"
  $BB unzip -o "$1" "$2" -p >"$3"
}

exit_install() {
  ui_print " "
  wipedalvik=$(ReadConfigValue "WipeDalvikCache" "$nikgapps_config_file_name")
  addToLog "- WipeDalvikCache value: $wipedalvik"
  if [ "$wipedalvik" != 0 ]; then
    ui_print "- Wiping dalvik-cache"
    rm -rf "/data/dalvik-cache"
  fi
  ui_print "- Finished Installation"
  ui_print " "
  copy_logs
  restore_env
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
  addToGeneralLog "- checking if $dev is block" "$mountLog"
  if [ -b "$dev" ]; then
    addToGeneralLog "- Block Dev: $dev" "$mountLog"
    echo "$dev"
  fi
}

find_config_path() {
  local config_dir_list="/tmp:$TMPDIR:$ZIPDIR:/sdcard1:/sdcard1/NikGapps:/sdcard:/sdcard/NikGapps:/storage/emulated:/storage/emulated/NikGapps:$COMMONDIR"
  local IFS=':'
  for location in $config_dir_list; do
    if [ -f "$location/$1" ]; then
      echo "$location/$1"
      return
    fi
  done
}

find_config() {
  mkdir -p "$nikGappsDir" "$addonDir" "$logDir" "$package_logDir" "$addon_scripts_logDir" "$TMPDIR/addon"
  ui_print " "
  ui_print "--> Finding config files"
  nikgapps_config_file_name="$nikGappsDir/nikgapps.config"
  unpack "afzc/nikgapps.config" "$COMMONDIR/nikgapps.config"
  unpack "afzc/debloater.config" "$COMMONDIR/debloater.config"
  use_zip_config=$(ReadConfigValue "use_zip_config" "$COMMONDIR/nikgapps.config")
  addToLog "- use_zip_config=$use_zip_config"
  if [ "$use_zip_config" = "1" ]; then
    ui_print "- Using config file from the zip"
    nikgapps_config_file_name="$COMMONDIR/nikgapps.config"
    debloater_config_file_name="$COMMONDIR/debloater.config"
  else
    found_config="$(find_config_path nikgapps.config)"
    if [ "$found_config" ]; then
      nikgapps_config_file_name="$found_config"
      addToLog "- Found custom location - $found_config of nikgapps.config"
      copy_file "$found_config" "$nikGappsDir/nikgapps.config"
    fi
    nikgapps_config_dir=$(dirname "$nikgapps_config_file_name")
    debloater_config_file_name="/sdcard/NikGapps/debloater.config"
    found_config="$(find_config_path debloater.config)"
    if [ "$found_config" ]; then
      debloater_config_file_name="$found_config"
      addToLog "- Found custom location - $found_config of debloater.config"
      copy_file "$found_config" "$nikGappsDir/debloater.config"
    fi
    nikgappsConfig="$sdcard/NikGapps/nikgapps.config"
    debloaterConfig="$sdcard/NikGapps/debloater.config"
    if [ ! -f $nikgappsConfig ]; then
      unpack "afzc/nikgapps.config" "/sdcard/NikGapps/nikgapps.config"
      [ ! -f "/sdcard/NikGapps/nikgapps.config" ] && unpack "afzc/nikgapps.config" "/storage/emulated/NikGapps/nikgapps.config"
      addToLog "nikgapps.config is copied to $nikgappsConfig"
    fi
    if [ ! -f $debloaterConfig ]; then
      unpack "afzc/debloater.config" "$COMMONDIR/debloater.config"
      unpack "afzc/debloater.config" "/sdcard/NikGapps/debloater.config"
      [ ! -f "/sdcard/NikGapps/debloater.config" ] && unpack "afzc/debloater.config" "/storage/emulated/NikGapps/debloater.config"
      addToLog "debloater.config is copied to $debloaterConfig"
    fi
  fi

  test "$zip_type" != "debloater" && ui_print "- nikgapps.config used from $nikgapps_config_file_name"
  test "$zip_type" = "debloater" && ui_print "- debloater.config used from $debloater_config_file_name"
}

find_device_block() {
  device_ab=$(getprop ro.build.ab_update 2>/dev/null)
  dynamic_partitions=$(getprop ro.boot.dynamic_partitions)
  [ -z "$dynamic_partitions" ] && dynamic_partitions="false"
  addToGeneralLog "- variable dynamic_partitions = $dynamic_partitions" "$mountLog"
  BLK_PATH=/dev/block/bootdevice/by-name
  if [ -d /dev/block/mapper ]; then
    dynamic_partitions="true"
    BLK_PATH="/dev/block/mapper"
    addToGeneralLog "- Directory method! Device with dynamic partitions Found" "$mountLog"
  else
    addToGeneralLog "- Device doesn't have dynamic partitions" "$mountLog"
  fi


  SLOT=$(find_slot)
  if [ -n "$SLOT" ]; then
    if [ "$SLOT" = "_a" ]; then
      SLOT_SUFFIX="_a"
    else
      SLOT_SUFFIX="_b"
    fi
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
  if [ "$zip_type" = "addon" ]; then
    ui_print "- Addon Size: $gapps_size KB"
  elif [ "$zip_type" = "gapps" ]; then
    ui_print "- Gapps Size: $gapps_size KB"
  elif [ "$zip_type" = "sideload" ]; then
    ui_print "- Package Size: $gapps_size KB"
  fi
}

find_install_mode() {
  if [ "$clean_flash_only" = "true" ] && [ "$install_type" = "dirty" ]; then
    prop_file_exists="false"
    for i in "$system/etc/permissions" "$system/product/etc/permissions" "$system/system_ext/etc/permissions"; do
      if [ -f "$i/$package_title.prop" ]; then
        addToLog "- Found $i/$package_title.prop" "$package_title"
        prop_file_exists="true"
        break
      fi
    done
    if [ "$prop_file_exists" = "false" ]; then
      test "$zip_type" = "gapps" && ui_print "- Cannot dirty flash, wipe /data to install $package_title" && return
      test "$zip_type" = "addon" && abort "- Cannot flash $package_title now as you will run into issues! Wipe /data if you still want to install it. You must always flash $package_title before booting into Rom!"
    fi
  fi
  addToLog "----------------------------------------------------------------------------" "$package_title"
  ui_print "- Installing $package_title" "$package_logDir/$package_title.log"
  install_package
  delete_recursive "$pkgFile"
  delete_recursive "$TMPDIR/$pkgContent"
}

find_install_type() {
  install_type="clean"
  for i in $(find /data -iname "runtime-permissions.xml" 2>/dev/null;); do
    if [ -e "$i" ]; then
      install_type="dirty"
      value=$(ReadConfigValue "WipeRuntimePermissions" "$nikgapps_config_file_name")
      [ -z "$value" ] && value=0
      addToLog "- runtime-permissions.xml found at $i with wipe permission $value"
      if [ "$value" = "1" ]; then
        rm -rf "$i"
        ui_print "- Wiped RuntimePermissions"
        install_type="now clean"
      fi
    fi;
  done
  ui_print "- Install Type is $install_type"
}

find_log_directory() {
  value=$(ReadConfigValue "LogDirectory" "$nikgapps_config_file_name")
  addToLog "- LogDirectory=$value"
  [ "$value" = "default" ] && value="$nikGappsDir"
  [ -z "$value" ] && value="$nikGappsDir"
  nikgapps_log_dir="$value"
}

find_partitions_type() {
  addToGeneralLog "- Finding partition type for /system" "$mountLog"
  SYSTEM_BLOCK=$(find_block "system")
  [ -n "$SYSTEM_BLOCK" ] && addToGeneralLog "- Found block for /system" "$mountLog"
  system="/system"
  system_size=$(get_available_size_again "/system")
  [ "$system_size" != "0" ] && addToGeneralLog "- /system is mounted as dedicated partition" "$mountLog"
  is_system_writable="$(is_mounted_rw "$system" 2>/dev/null)"
  [ ! "$is_system_writable" ] && system=""
  addToGeneralLog "- system=$system is writable? $is_system_writable" "$mountLog"
  [ -f "/system/build.prop" ] && addToGeneralLog "- /system/build.prop exists" "$mountLog"

  for partition in "product" "system_ext"; do
    addToGeneralLog "----------------------------------------------------------------------------" "$mountLog"
    addToGeneralLog "- Finding partition type for /$partition" "$mountLog"
    mnt_point="/$partition"
    already_mounted=false
    already_symlinked=false
    mountpoint "$mnt_point" >/dev/null 2>&1 && already_mounted=true && addToGeneralLog "- $mnt_point already mounted!" "$mountLog"
    [ -L "$system$mnt_point" ] && already_symlinked=true && addToGeneralLog "- $system$mnt_point symlinked!" "$mountLog"
    case "$partition" in
      "product")
        # set the partition default to /system/$partition
        product="$system/product"
        product_size=0
        PRODUCT_BLOCK=$(find_block "$partition")
        # if block exists, set the partition to /$partition and get it's size
        if [ -n "$PRODUCT_BLOCK" ]; then
          addToGeneralLog "- Found block for $mnt_point" "$mountLog"
          product="/product"
          product_size=$(get_available_size_again "/product")
          ui_print "- /$partition is a dedicated partition" "$mountLog"
        else
          addToGeneralLog "- /$partition block not found in this device" "$mountLog"
        fi
        # check if partition is symlinked, if it is, set the partition back to /system/$partition
        if [ -L "$system$mnt_point" ]; then
          addToGeneralLog "- $system$mnt_point symlinked!" "$mountLog"
          product=$system$mnt_point
          ui_print "- /$partition is symlinked to $system$mnt_point" "$mountLog"
        fi
        # check if the partitions are writable
        is_product_writable="$(is_mounted_rw "$product" 2>/dev/null)"
        [ ! "$is_product_writable" ] && product=""
        addToGeneralLog "- product=$product is writable? $is_product_writable" "$mountLog"
      ;;
      "system_ext")
        # set the partition default to /system/$partition
        system_ext="$system/system_ext"
        system_ext_size=0
        SYSTEM_EXT_BLOCK=$(find_block "$partition")
        # if block exists, set the partition to /$partition and get it's size
        if [ -n "$SYSTEM_EXT_BLOCK" ]; then
          addToGeneralLog "- Found block for $mnt_point" "$mountLog"
          system_ext="/system_ext"
          system_ext_size=$(get_available_size_again "/system_ext")
          ui_print "- /$partition is a dedicated partition" "$mountLog"
        else
          addToGeneralLog "- /$partition block not found in this device" "$mountLog"
        fi
        # check if partition is symlinked, if it is, set the partition back to /system/$partition
        if [ -L "$system$mnt_point" ]; then
          addToGeneralLog "- $system$mnt_point symlinked!" "$mountLog"
          system_ext=$system$mnt_point
          ui_print "- /$partition is symlinked to $system$mnt_point" "$mountLog"
        fi
        # check if the partitions are writable
        is_system_ext_writable="$(is_mounted_rw "$system_ext" 2>/dev/null)"
        [ ! "$is_system_ext_writable" ] && system_ext=""
        addToGeneralLog "- system_ext=$system_ext is writable? $is_system_ext_writable" "$mountLog"
      ;;
    esac
  done
  # calculate gapps space and check if default partition has space
  # set a secondary partition to install if the space runs out
}

find_prop_match() {
    if [ ! -f "$3" ]; then
      echo ""
    else
      dataTypePath=$(echo "$1" | sed "s|^$system/||")
      dataTypePath=${dataTypePath#/}
      test=$(grep -n "$2=$dataTypePath" "$3" | cut -d: -f1)
      [ -n "$test" ] && echo "$dataTypePath" || echo ""
    fi
}

find_product_prefix() {
  case "$1" in
    *"/product") product_prefix="product/" ;;
    *"/system_ext") product_prefix="system_ext/" ;;
    *) product_prefix="" ;;
  esac
  addToGeneralLog "- product_prefix=$product_prefix" "$mountLog"
  echo "$product_prefix"
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
  [ "$total_size" = "0" ] && addToLog "- No space left on device"
  [ "$total_size" = "0" ] && ui_print "- Unable to find space"
}

find_zip_type() {
  addToLog "- Finding zip type"
  if [ "$(contains "-arm64-" "$actual_file_name")" = "true" ]; then
    zip_type="gapps"
  elif [ "$(contains "Debloater" "$actual_file_name")" = "true" ]; then
    zip_type="debloater"
  elif [ "$(contains "Addon" "$actual_file_name")" = "true" ]; then
    zip_type="addon"
  elif [ "$(contains "package" "$actual_file_name")" = "true" ]; then
    zip_type="sideload"
  else
    zip_type="unknown"
  fi
  sideloading=false
  if [ "$(contains "package" "$ZIPNAME")" = "true" ]; then
    sideloading=true
  fi
  addToLog "- Zip Type is $zip_type"
  addToLog "- Sideloading is $sideloading"
}

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
  grep -v "^#" /etc/recovery.fstab | grep "[[:blank:]]$1[[:blank:]]" | tail -n1 | tr -s [:blank:] ' ' | cut -d' ' -f1
}

get_file_prop() {
  grep -m1 "^$2=" "$1" | cut -d= -f2
}

get_install_partition(){
  chain_partition=$2
  size_required=$3
  pkg_name=$4
  case $1 in
    system)
      install_partition=""
      system_available_size=$(get_available_size_again "/system" "$pkg_name")
      addToLog "- fetched the system size to check if it's enough: $system_available_size" "$pkg_name"
      if [ $system_available_size -gt $size_required ]; then
        addToLog "- it's big enough" "$pkg_name"
        install_partition="$system"
      else
        addToLog "- check if chain_partition contains -system" "$pkg_name"
        if [ "$(contains "-system" "$chain_partition")" = "true" ]; then
          addToLog "- we've reached a complete loop, no space available now" "$pkg_name"
          install_partition="-1"
        else
          addToLog "- system is too big, let's try the system_ext (which will loop through product and system to confirm no partitions are big enough)" "$pkg_name"
          if [ -n "$SYSTEM_EXT_BLOCK" ] || [ -n "$PRODUCT_BLOCK" ]; then
            install_partition="$(get_install_partition system_ext system_ext-$chain_partition $size_required "$pkg_name")"
          else
            addToLog "- no space available" "$pkg_name"
            install_partition="-1"
          fi
        fi
      fi
    ;;
    product)
      install_partition="" 
      addToLog "- if product is a block, we will check if it's big enough" "$pkg_name"
      if [ -n "$PRODUCT_BLOCK" ]; then
        product_available_size=$(get_available_size_again "/product" "$pkg_name")
        addToLog "- fetched the product size to check if it's enough: $product_available_size" "$pkg_name"
        if [ $product_available_size -gt $size_required ]; then
          addToLog "- it's big enough, we'll use it" "$pkg_name"
          install_partition="$product"
        else
          addToLog "- check if chain_partition ends with -product" "$pkg_name"
          if [ "$(contains "-product" "$chain_partition")" = "true" ]; then
            addToLog "- we've reached a complete loop, no space available now" "$pkg_name"
            install_partition="-1"
          else
            addToLog "- it's not, we'll try system" "$pkg_name"
            install_partition="$(get_install_partition system system-$chain_partition $size_required "$pkg_name")"
          fi
        fi
      else
        addToLog "- product is not a block, we'll try system and install to /system/product as it will take up system space" "$pkg_name"
        system_available_size=$(get_available_size_again "/system" "$pkg_name")
        addToLog "- fetched the system size to check if it's enough: $system_available_size" "$pkg_name"
        if [ $system_available_size -gt $size_required ]; then
          addToLog "- system is big enough, we'll use it" "$pkg_name"
          install_partition="/system/product"
        else
          addToLog "- if product is not a block and system is not big enough, we're out of options" "$pkg_name"
          install_partition="-1"
        fi
      fi
    ;;
    system_ext) 
      install_partition=""
      addToLog "- if system_ext is a block, we will check if it's big enough" "$pkg_name"
      if [ -n "$SYSTEM_EXT_BLOCK" ]; then
        system_ext_available_size=$(get_available_size_again "/system_ext" "$pkg_name")
        addToLog "- fetched the system_ext size to check if it's enough: $system_ext_available_size" "$pkg_name"
        if [ $system_ext_available_size -gt $size_required ]; then
          addToLog "- it's big enough, we'll use it" "$pkg_name"
          install_partition="$system_ext"
        else
          addToLog "- check if chain_partition ends with -system_ext" "$pkg_name"
          if [ "$(contains "-system_ext" "$chain_partition")" = "true" ]; then
            addToLog "- we've reached a complete loop, no space available now" "$pkg_name"
            install_partition="-1"
          else
            install_partition="$(get_install_partition product product-$chain_partition $size_required "$pkg_name")"
          fi
        fi
      else
        addToLog "- system_ext isn't a block, we'll try product and see if it has space" "$pkg_name"
        if [ -n "$PRODUCT_BLOCK" ]; then
          install_partition="$(get_install_partition product product-$chain_partition $size_required "$pkg_name")"
        else
          addToLog "- product isn't a block, we'll try system and see if it has space" "$pkg_name"
          system_available_size=$(get_available_size_again "/system" "$pkg_name")
          addToLog "- fetched the system size to check if it's enough: $system_available_size" "$pkg_name"
          if [ $system_available_size -gt $size_required ]; then
            addToLog "- system is big enough, we'll use it" "$pkg_name"
            install_partition="$system_ext"
          else
            addToLog "- if system_ext is not a block and system is not big enough, we're out of options" "$pkg_name"
            install_partition="-1"
          fi
        fi
      fi
    ;;
  esac
  if [ -f "$nikgapps_config_file_name" ]; then
    case "$install_partition_val" in
      "default") addToLog "- InstallPartition is default" "$pkg_name" ;;
      "system") install_partition=$system ;;
      "product") install_partition=$product ;;
      "system_ext") install_partition=$system_ext ;;
      "data") install_partition="/data/extra" ;;
      /*) install_partition=$install_partition_val ;;
    esac
    addToLog "- InstallPartition = $install_partition" "$pkg_name"
  else
    addToLog "- nikgapps.config file doesn't exist!" "$pkg_name"
  fi
  echo "$install_partition"
}

get_package_progress(){
  for i in $ProgressBarValues; do
      if [ $(echo $i | cut -d'=' -f1) = "$1" ]; then
          echo $i | cut -d'=' -f2
          return
      fi
  done
  echo 0
}

get_prop() {
  local propdir propfile propval
  for propdir in /system /vendor /odm /product /system/product /system/system_ext /system_root /; do
    for propfile in build.prop default.prop; do
      test "$propval" && break 2 || propval="$(get_file_prop $propdir/$propfile "$1" 2>/dev/null)"
    done
  done
  addToLog "- propvalue $1 = $propval"
  # if propval is no longer empty output current result; otherwise try to use recovery's built-in getprop method
  [ -z "$propval" ] && propval=$(getprop "$1")
  addToLog "- Recovery getprop used $1=$propval"
  test "$propval" && echo "$propval" || echo ""
}

get_total_available_size(){
  system_available_size=0
  product_available_size=0
  system_ext_available_size=0
  # system would always be block
  system_available_size=$(get_available_size_again "/system")
  [ -n "$SYSTEM_EXT_BLOCK" ] && system_ext_available_size=$(get_available_size_again "/system_ext")
  [ -n "$PRODUCT_BLOCK" ] && product_available_size=$(get_available_size_again "/product")
  addToLog "- total_available_size=$system_available_size + $product_available_size + $system_ext_available_size"
  total_available_size=$(($system_available_size + $product_available_size + $system_ext_available_size))
  addToLog "- total available size = $total_available_size"
  echo "$total_available_size"
}

install_app_set() {
  appset_name="$1"
  packages_in_appset="$2"
  extn="$3"
  addToLog "----------------------------------------------------------------------------"
  value=1
  if [ -f "$nikgapps_config_file_name" ]; then
    value=$(ReadConfigValue "$appset_name" "$nikgapps_config_file_name")
    if [ "$value" = "" ]; then
      value=1
    fi
  fi
  addToLog "- Current Appset=$appset_name, value=$value"
  case "$value" in
    "0")
      ui_print "x Skipping $appset_name"
    ;;
    "-1")
      addToLog "- $appset_name is disabled"
      for i in $packages_in_appset; do
        current_package_title=$(echo "$i" | cut -d',' -f1)
        uninstall_the_package "$appset_name" "$current_package_title" "$extn"
      done
    ;;
    *)
      case "$mode" in
        "uninstall_by_name")
          for k in $packages_in_appset; do
            current_package_title=$(echo "$k" | cut -d',' -f1)
            uninstall_the_package "$appset_name" "$current_package_title" "$extn"
          done
        ;;
        "uninstall")
          for k in $packages_in_appset; do
            current_package_title=$(echo "$k" | cut -d',' -f1)
            [ -z "$value" ] && value=$(ReadConfigValue "$current_package_title" "$nikgapps_config_file_name")
            [ -z "$value" ] && value=1
            [ "$value" -eq -1 ] && uninstall_the_package "$appset_name" "$current_package_title" "$extn"
          done
        ;;
        "install")
          for i in $packages_in_appset; do
            current_package_title=$(echo "$i" | cut -d',' -f1)
            addToLog "----------------------------------------------------------------------------" "$current_package_title"
            addToLog "----------------------------------------------------------------------------"
            addToLog "- Working for $current_package_title" "$current_package_title"
            addToLog "- Working for $current_package_title"
            value=$(ReadConfigValue ">>$current_package_title" "$nikgapps_config_file_name")
            [ -z "$value" ] && value=$(ReadConfigValue "$current_package_title" "$nikgapps_config_file_name")
            [ -z "$value" ] && value=1
            if [ "$value" -ge 1 ]; then
              package_size=$(echo "$i" | cut -d',' -f2)
              addToLog "- package_size = $package_size" "$current_package_title"
              default_partition=$(echo "$i" | cut -d',' -f3)
              addToLog "- default_partition = $default_partition" "$current_package_title"
              case "$default_partition" in
                "system_ext")
                [ $androidVersion -le 10 ] && default_partition=product && addToLog "- default_partition is overridden" "$current_package_title"
                ;;
              esac
              addToLog "----------------------------------------------------------------------------" "$current_package_title"
              install_partition=$(get_install_partition "$default_partition" "$default_partition" "$package_size" "$current_package_title")
              if [ "$install_partition" = "-1" ]; then
                ui_print "- Storage is full, uninstalling to free up space"
                uninstall_the_package "$appset_name" "$current_package_title" "$extn"
                addToLog "----------------------------------------------------------------------------" "$current_package_title"
                install_partition=$(get_install_partition "$default_partition" "$default_partition" "$package_size" "$current_package_title")
              fi
              addToLog "- $current_package_title required size: $package_size Kb, installing to $install_partition ($default_partition)" "$current_package_title"
              if [ "$install_partition" != "-1" ]; then
                size_before=$(calculate_space_before "$current_package_title" "$install_partition")
                install_the_package "$appset_name" "$i" "$current_package_title" "$value" "$install_partition" "$extn"
                size_after=$(calculate_space_after "$current_package_title" "$install_partition" "$size_before" "$package_size")
              else
                ui_print "x Skipping $current_package_title as no space is left" "$package_logDir/$current_package_title.log"
              fi
            elif [ "$value" -eq -1 ] ; then
              addToLog "- uninstalling $current_package_title" "$current_package_title"
              uninstall_the_package "$appset_name" "$current_package_title" "$extn"
            elif [ "$value" -eq 0 ] ; then
              ui_print "x Skipping $current_package_title" "$package_logDir/$current_package_title.log"
            fi
          done
        ;;
        *)
          addToLog "- Invalid mode $mode"
        ;;
      esac
    ;;
  esac
}

install_the_package() {
  appset_name="$1"
  default_partition=$(echo "$2" | cut -d',' -f3)
  package_name="$3"
  config_value="$4"
  install_partition="$5"
  [ -z "$6" ] && extn=".zip" || extn="$6"
  addToLog "- Default Extn=$extn" "$package_name"
  case "$extn" in
    .*) ;;
    *) extn=".$extn" ;;
  esac
  addToLog "- Install_Partition=$install_partition" "$package_name"
  addToLog "- Extn=$extn" "$package_name"
  pkgFile="$TMPDIR/$package_name$extn"
  pkgContent="pkgContent"
  unpack_pkg "AppSet/$1/$package_name$extn" "$pkgFile" "$package_name"
  case $extn in
    ".zip")
      extract_pkg "$pkgFile" "installer.sh" "$TMPDIR/$pkgContent/installer.sh" "$package_name"
    ;;
    ".tar.xz")
      delete_recursive "$TMPDIR/$pkgContent"
      extract_tar_xz "$pkgFile" "$TMPDIR/$pkgContent" "$package_name"
    ;;
  esac
  chmod 755 "$TMPDIR/$pkgContent/installer.sh"
  # shellcheck source=src/installer.sh
  . "$TMPDIR/$pkgContent/installer.sh" "$config_value" "$nikgapps_config_file_name" "$install_partition"

  set_progress "$(get_package_progress "$package_name")"
}

install_file() {
  if [ "$mode" != "uninstall" ]; then
    # $1 will start with ___ which needs to be skipped so replacing it with blank value
    blank=""
    file_location=$(echo "$1" | sed "s/___/$blank/" | sed "s/___/\//g")
    enforced_partition=$(echo "$file_location" | cut -d'/' -f 1)
    case "$enforced_partition" in
      "system"|"system_ext"|"product"|"vendor")
        addToLog "- /$file_location is forced to be installed in $enforced_partition" "$package_title"
        install_location="/$file_location"
        ;;
      *)
        install_location="$install_partition/$file_location"
        ;;
    esac
    # Make sure the directory exists, if not, copying the file would fail
    mkdir -p "$(dirname "$install_location")"
    set_perm 0 0 0755 "$(dirname "$install_location")"
    # unpacking of package
    addToLog "- Unpacking $pkgFile" "$package_title"
    addToLog "  -> copying $1" "$package_title"
    addToLog "  -> to $install_location" "$package_title"
    case $extn in
      ".zip")
        $BB unzip -o "$pkgFile" "$1" -p >"$install_location"
      ;;
      ".tar.xz")
        copy_file "$TMPDIR/$pkgContent/$1" "$install_location"
      ;;
    esac
    # post unpack operations
    if [ -f "$install_location" ]; then
      addToLog "- File Successfully Written!" "$package_title"
      # It's important to set selinux policy
      case $install_location in
        *)
          ch_con system "$install_location"
          addToLog "- ch_con with ${1} for $2" "$package_title"
        ;;
      esac
      set_perm 0 0 0644 "$install_location"
      # Addon stuff!
      case "$enforced_partition" in
      "system"|"system_ext"|"product"|"vendor")
        installPath=$(echo "$file_location" | sed "s/$enforced_partition\///")
        installPath="$installPath"
        ;;
      *)
        case "$install_partition" in
            *"/product") installPath="product/$file_location" ;;
            *"/system_ext") installPath="system_ext/$file_location" ;;
            *) installPath="$file_location" ;;
        esac
        ;;
      esac
      update_prop "$installPath" "install" "$propFilePath" "$package_title"
      addToLog "- InstallPath=$installPath" "$package_title"
    else
      ui_print "- Failed to write $install_location" "$package_logDir/$package_title.log"
      ui_print " " "$package_logDir/$package_title.log"
      find_system_size
      abort "Installation Failed! Looks like Storage space is full!"
    fi
  fi
}

is_on_top_of_nikgapps() {
  nikgapps_present=false
  # shellcheck disable=SC2143
  if [ "$(grep 'allow-in-power-save package=\"com.mgoogle.android.gms\"' "$system"/etc/sysconfig/*.xml)" ] ||
        [ "$(grep 'allow-in-power-save package=\"com.mgoogle.android.gms\"' "$system"/product/etc/sysconfig/*.xml)" ]; then
    nikgapps_present=true
  fi
  addToLog "- Is on top of NikGapps: $nikgapps_present"
  if [ "$nikgapps_present" != "true" ]; then
    abort "This Addon can only be flashed on top of NikGapps"
  fi
}

# Check if the partition is mounted
is_mounted() {
  addToGeneralLog "- Checking if $1 is mounted" "$mountLog"
  $BB mount | $BB grep -q " $1 ";
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
}

# Read the config file from (Thanks to xXx @xda)
ReadConfigValue() {
  value=$(sed -e '/^[[:blank:]]*#/d;s/[\t\n\r ]//g;/^$/d' "$2" | grep -m 1 "^$1=" | cut -d'=' -f 2)
  echo "$value"
  return $?
}

delete_overlays(){
  overlays_deleted=""
  addToLog "- Deleting Overlays"
  for i in $(find "$system/product/overlay" "$system/system_ext/overlay" "/product/overlay" "/system_ext/overlay" -type f -name "*$1*.apk" 2>/dev/null); do
    addToLog "- Deleting $i" "$3"
    rm -rf "$i"
    overlays_deleted="$overlays_deleted":"$i"
  done
  if [ -n "$overlays_deleted" ]; then
    addToLog "- Deleted Overlays: $overlays_deleted" "$3"
    OLD_IFS="$IFS"
    IFS=":"
    for i in $overlays_deleted; do
      if [ -n "$i" ]; then
        update_prop "$i" "delete" "$2" "$3"
      fi
    done
    IFS="$OLD_IFS"
  else
    addToLog "- No $1 overlay to remove" "$3"
  fi
}

RemoveAospAppsFromRom() {
  addToLog "- Removing AOSP App from Rom" "$3"
  if [ "$configValue" -eq 2 ]; then
    addToLog "- Not creating addon.d script for $*" "$3"
  else
    deleted_folders=$(clean_recursive "$1" "$3")
    if [ -n "$deleted_folders" ]; then
      addToLog "- Removed folders: $deleted_folders" "$3"
      OLD_IFS="$IFS"
      IFS=":"
      for i in $deleted_folders; do
        if [ -n "$i" ]; then
          update_prop "$i" "delete" "$2" "$3"
        fi
      done
      IFS="$OLD_IFS"
    else
      match=$(find_prop_match "$1" "delete" "$3")
      [ -z "$match" ] && update_prop "$1" "forceDelete" "$2" "$3"
      addToLog "- No $1 folders to remove" "$3"
    fi
  fi
}

set_perm() {
  chown "$1:$2" "$4"
  chmod "$3" "$4"
}

set_prop() {
  property="$1"
  value="$2"
  test -z "$3" && file_location="${install_partition}/build.prop" || file_location="$3"
  test ! -f "$file_location" && touch "$file_location" && set_perm 0 0 0600 "$file_location"
  addToLog "- Setting Property ${1} to ${2} in ${file_location}"
  if grep -q "${property}" "${file_location}"; then
    addToLog "- Updating ${property} to ${value} in ${file_location}"
    sed -i "s/\(${property}\)=.*/\1=${value}/g" "${file_location}"
  else
    addToLog "- Adding ${property} to ${value} in ${file_location}"
    echo "${property}=${value}" >>"${file_location}"
  fi
}

show_device_info() {
  ui_print " "
  ui_print "--> Fetching Device Information"
  mount_system_source
  sdkVersion=$(get_prop "ro.build.version.sdk")
  androidVersion=$(get_prop "ro.build.version.release")
  model=$(get_prop "ro.product.system.model")
  series=$(get_prop "ro.display.series")
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
  addToLog "- Series: $series"
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

# Setting up mount point
setup_mountpoint() {
  addToGeneralLog "- Setting up mount point $1 before actual mount" "$mountLog"
  test -L "$1" && $BB mv -f "$1" "${1}"_link;
  if [ ! -d "$1" ]; then
    rm -f "$1";
    mkdir -p "$1";
  fi;
}

restore_env() {
  $BOOTMODE && return 1;
  local dir;
  unset -f getprop;
  [ "$OLD_LD_PATH" ] && export LD_LIBRARY_PATH=$OLD_LD_PATH;
  [ "$OLD_LD_PRE" ] && export LD_PRELOAD=$OLD_LD_PRE;
  [ "$OLD_LD_CFG" ] && export LD_CONFIG_FILE=$OLD_LD_CFG;
  unset OLD_LD_PATH OLD_LD_PRE OLD_LD_CFG;
  umount_all;
  [ -L /etc_link ] && $BB rm -rf /etc/*;
  (for dir in /etc /apex /system_root /system /vendor /product /system_ext /persist; do
    if [ -L "${dir}_link" ]; then
      rmdir $dir;
      $BB mv -f ${dir}_link $dir;
    fi;
  done;
  $BB umount -l /dev/random) 2>/dev/null;
}

update_prop() {
  propFilePath=$1
  dataPath=$1
  dataType=$2
  log_path=$4
  [ -n "$3" ] && propFilePath=$3
  if [ ! -f "$propFilePath" ]; then
    touch "$propFilePath"
    addToLog "- Creating $propFilePath" "$log_path"
  fi
  dataTypePath=$(echo "$dataPath" | sed "s|^$system/||")
  dataTypePath=${dataTypePath#/}
  line=$(grep -n "$dataType=$dataTypePath" "$propFilePath" | cut -d: -f1)
  if [ -z "$line" ]; then
    echo "$dataType=$dataTypePath" >> "$propFilePath"
    addToLog "- $dataType=$dataTypePath >> $propFilePath" "$log_path"
  else
    addToLog "- $dataTypePath $dataType-ed already in $propFilePath" "$log_path"
  fi
}

uninstall_file() {
  addToLog "- Uninstalling $1" "$2"
  # $1 will start with ___ which needs to be skipped so replacing it with blank value
  blank=""
  file_location=$(echo "$1" | sed "s/___/$blank/" | sed "s/___/\//g")
  # For Devices having symlinked product and system_ext partition
  for sys in "/system"; do
    for subsys in "/system" "/product" "/system_ext"; do
      if [ -f "${sys}${subsys}/${file_location}" ]; then
        addToLog "- deleting ${sys}${subsys}/${file_location}" "$2"
        delete_recursive "${sys}${subsys}/${file_location}"
      fi;
    done
  done
  # For devices having dedicated product and system_ext partitions
  for subsys in "/system" "/product" "/system_ext"; do
    if [ -f "${subsys}/${file_location}" ]; then
      addToLog "- deleting ${subsys}/${file_location}"
      delete_recursive "${subsys}/${file_location}"
    fi
  done
}

uninstall_the_package() {
  package_name="$2"
  extn="$3"
  case "$extn" in
    .*) ;;
    *) extn=".$extn" ;;
  esac
  ui_print "- Uninstalling $package_name"
  pkgFile="$TMPDIR/$package_name$extn"
  pkgContent="pkgContent"
  unpack_pkg "AppSet/$1/$package_name$extn" "$pkgFile" "$package_name"
  case $extn in
    ".zip")
      extract_pkg "$pkgFile" "uninstaller.sh" "$TMPDIR/$pkgContent/uninstaller.sh" "$package_name"
    ;;
    ".tar.xz")
      delete_recursive "$TMPDIR/$pkgContent"
      extract_tar_xz "$pkgFile" "$TMPDIR/$pkgContent" "$package_name"
    ;;
  esac
  chmod 755 "$TMPDIR/$pkgContent/uninstaller.sh"
  # shellcheck source=src/uninstaller.sh
  . "$TMPDIR/$pkgContent/uninstaller.sh"
  set_progress $(get_package_progress "$package_name")
  delete_recursive "$pkgFile"
  delete_recursive "$TMPDIR/$pkgContent"
}