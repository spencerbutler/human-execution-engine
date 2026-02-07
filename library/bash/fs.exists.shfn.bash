# fs.exists.shfn.bash
# stage: ~/.hee/library/bash/
# no set -e/-u/pipefail

sb_fs_exists() {
  p="$1"
  if [ -e "$p" ]; then
    sb_return_ok
    echo "SB_OP=fs.exists"
    echo "SB_PATH=$p"
    echo "SB_EXISTS=1"
    return 0
  fi

  sb_return_ok
  echo "SB_OP=fs.exists"
  echo "SB_PATH=$p"
  echo "SB_EXISTS=0"
  return 0
}
