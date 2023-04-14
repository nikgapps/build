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
  ui_print() { echo "$1"; test "$nikGappsAddonLogFile" && echo "$(date +%Y_%m_%d_%H_%M_%S): $1" >> "$nikGappsAddonLogFile"; }
else
  ui_print() {
    echo -e "ui_print $1\nui_print" >> /proc/self/fd/$OUTFD; test "$nikGappsAddonLogFile" && echo "$(date +%Y_%m_%d_%H_%M_%S): $1" >> "$nikGappsAddonLogFile";
   }
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

CopyFile() {
  if [ -f "$1" ]; then
    mkdir -p "$(dirname "$2")"
    cp -f "$1" "$2"
  fi
}

delete_in_system(){
  for i in $1; do
    addToLog "- $2 $i"
    if [ "${i#*/*}" != "$i" ]; then
      delete_if_exists "/postinstall$S/$i" "/postinstall/$i" "$S/$i" "/$i"
    else
      for j in $(find "/system" "/product" "/system_ext" "/postinstall/system" "/postinstall/product" "/postinstall/system_ext" -iname "$i"); do
        delete_if_exists "$j"
      done
    fi
  done
}

delete_if_exists(){
  for i in "$@"; do
    addToLog "- Checking if $i exists"
    if [ -f "$i" ] || [ -d "$i" ]; then
      addToLog "- Found, deleting $i"
      rm -rf "$i"
    fi
  done
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

[ -z $nikgapps_config_file_name ] && find_config

[ -z $execute_config ] && execute_config=$(ReadConfigValue "execute.d" "$nikgapps_config_file_name")
[ "$execute_config" != "0" ] && execute_config=1

