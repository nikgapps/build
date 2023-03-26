#!/sbin/sh
configValue="$1"
nikgapps_config_file_name="$2"
install_partition="$3"

make_dir() {
  addToLog "- Creating Directory: $install_partition/$1" "$package_title"
  mkdir -p "$install_partition/$1"
  set_perm 1000 1000 0755 "$install_partition/$1"
}
