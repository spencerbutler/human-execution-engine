# fs.readlink.shfn.bash
# stage: ~/.hee/library/bash/
# no set -e/-u/pipefail

sb_fs_readlink() {
  p="$1"

  if [ ! -e "$p" ]; then
    sb_return_fail 2 "not_found"
    echo "SB_OP=fs.readlink" >&2
    echo "SB_PATH=$p" >&2
    return 2
  fi

  out="$(readlink -f -- "$p" 2>/dev/null)"
  r=$?
  if [ "$r" -ne 0 ] || [ -z "$out" ]; then
    sb_return_fail 2 "readlink_failed"
    echo "SB_OP=fs.readlink" >&2
    echo "SB_PATH=$p" >&2
    return 2
  fi

  sb_return_ok
  echo "SB_OP=fs.readlink"
  echo "SB_PATH=$p"
  echo "SB_TARGET=$out"
  return 0
}
