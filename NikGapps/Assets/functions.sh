# determine parent output fd and ui_print method
FD=1
# update-binary|updater <RECOVERY_API_VERSION> <OUTFD> <ZIPFILE>
OUTFD=$(ps | grep -v 'grep' | grep -oE 'update(.*) 3 [0-9]+' | cut -d" " -f3)
[ -z $OUTFD ] && OUTFD=$(ps -Af | grep -v 'grep' | grep -oE 'update(.*) 3 [0-9]+' | cut -d" " -f3)
# update_engine_sideload --payload=file://<ZIPFILE> --offset=<OFFSET> --headers=<HEADERS> --status_fd=<OUTFD>
[ -z $OUTFD ] && OUTFD=$(ps | grep -v 'grep' | grep -oE 'status_fd=[0-9]+' | cut -d= -f2)
[ -z $OUTFD ] && OUTFD=$(ps -Af | grep -v 'grep' | grep -oE 'status_fd=[0-9]+' | cut -d= -f2)
test "$verbose" -a "$OUTFD" && FD=$OUTFD
if [ -z $OUTFD ]; then
  ui_print() { echo "$1"; test "/sdcard/NikGapps/addonLogs/logfiles/NikGapps.log" && echo "$1" >> "/sdcard/NikGapps/addonLogs/logfiles/NikGapps.log"; }
else
  ui_print() { echo -e "ui_print $1\nui_print" >> /proc/self/fd/$OUTFD; test "/sdcard/NikGapps/addonLogs/logfiles/NikGapps.log" && echo "$1" >> "/sdcard/NikGapps/addonLogs/logfiles/NikGapps.log"; }
fi

if [ -d "/postinstall" ]; then
  P="/postinstall/system"
  T="/postinstall/tmp"
else
  P="$S"
  T="/tmp"
fi

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

clean_recursive () {
  func_result="$(beginswith / "$1")"
  addToLog "- Deleting $1 with func_result: $func_result"
  if [ "$func_result" = "true" ]; then
    addToLog "- Deleting $1"
    rm -rf "$1"
  else
    addToLog "- Deleting $1"
    # For OTA update
    for sys in "/postinstall" "/postinstall/system"; do
      for subsys in "/system" "/product" "/system_ext"; do
        for folder in "/app" "/priv-app"; do
          delete_recursive "$sys$subsys$folder/$1"
        done
      done
    done
    # For Devices having symlinked product and system_ext partition
    for sys in "$P" "/system" "/system_root"; do
      for subsys in "/system" "/product" "/system_ext"; do
        for folder in "/app" "/priv-app"; do
          delete_recursive "$sys$subsys$folder/$1"
        done
      done
    done
    # For devices having dedicated product and system_ext partitions
    for subsys in "$P" "/system" "/product" "/system_ext"; do
      for folder in "/app" "/priv-app"; do
        delete_recursive "$subsys$folder/$1"
      done
    done
  fi
}

CopyFile() {
  if [ -f "$1" ]; then
    mkdir -p "$(dirname "$2")"
    cp -f "$1" "$2"
  fi
}

delete_recursive() {
  addToLog "- rm -rf $*"
  rm -rf "$*"
}

find_config() {
  nikgapps_config_file_name="$nikGappsDir/nikgapps.config"
  for location in "/tmp" "/sdcard1" "/sdcard1/NikGapps" "/sdcard" "/storage/emulated/NikGapps" "/storage/emulated"; do
    if [ -f "$location/nikgapps.config" ]; then
      nikgapps_config_file_name="$location/nikgapps.config"
      break;
    fi
  done
}

# Read the config file from (Thanks to xXx @xda)
ReadConfigValue() {
  value=$(sed -e '/^[[:blank:]]*#/d;s/[\t\n\r ]//g;/^$/d' "$2" | grep "^$1=" | cut -d'=' -f 2)
  echo "$value"
  return $?
}

find_config

execute_config=$(ReadConfigValue "execute.d" "$nikgapps_config_file_name")
[ "$execute_config" != "0" ] && execute_config=1
addToLog "- execute_config = $execute_config"
addon_version_config=$(ReadConfigValue "addon_version.d" "$nikgapps_config_file_name")
[ -z "$addon_version_config" ] && addon_version_config=3
addToLog "- addon_version_config = $addon_version_config"
