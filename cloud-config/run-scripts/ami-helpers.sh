function copy_with_permission {
    src_file="$1"
    dest_file="$2"
    sudo -u root cp "$src_file" "$dest_file"
    sudo -u root chown root:elasticsearch "$dest_file"
}

function append_with_user {
  line="$1"
  user="$2"
  dest="$3"
  echo "$line" | sudo -u $user tee -a $dest
}