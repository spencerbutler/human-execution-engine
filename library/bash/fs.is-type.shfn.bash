# fs.is-type.shfn.bash
# stage: ~/.hee/library/bash/
# no set -e/-u/pipefail

sb_fs_is_file() {
  p="$1"
  if [ -f "$p" ]; then
    sb_return_ok
    echo "SB_OP=fs.is-file"
    echo "SB_PATH=$p"
    echo "SB_IS_FILE=1"
    return 0
  fi
  sb_return_ok
  echo "SB_OP=fs.is-file"
  echo "SB_PATH=$p"
  echo "SB_IS_FILE=0"
  return 0
}

sb_fs_is_dir() {
  p="$1"
  if [ -d "$p" ]; then
    sb_return_ok
    echo "SB_OP=fs.is-dir"
    echo "SB_PATH=$p"
    echo "SB_IS_DIR=1"
    return 0
  fi
  sb_return_ok
  echo "SB_OP=fs.is-dir"
  echo "SB_PATH=$p"
  echo "SB_IS_DIR=0"
  return 0
}
