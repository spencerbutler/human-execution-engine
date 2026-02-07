# fs.read.shfn.bash
# stage: ~/.hee/library/bash/
# no set -e/-u/pipefail

sb_fs_cat() {
  p="$1"
  cat "$p"
  r=$?
  if [ "$r" -ne 0 ]; then
    sb_return_fail "$r" "cat_failed"
    echo "SB_OP=fs.cat" >&2
    echo "SB_PATH=$p" >&2
    return "$r"
  fi
  sb_return_ok
  echo "SB_OP=fs.cat"
  echo "SB_PATH=$p"
  return 0
}

sb_fs_tail() {
  n="$1"
  p="$2"
  tail -n "$n" "$p"
  r=$?
  if [ "$r" -ne 0 ]; then
    sb_return_fail "$r" "tail_failed"
    echo "SB_OP=fs.tail" >&2
    echo "SB_PATH=$p" >&2
    return "$r"
  fi
  sb_return_ok
  echo "SB_OP=fs.tail"
  echo "SB_PATH=$p"
  echo "SB_N=$n"
  return 0
}

sb_fs_sha256() {
  if [ "$#" -lt 1 ]; then
    sb_return_fail 2 "usage"
    echo "SB_HINT=shellboss fs sha256 <path> [path...]" >&2
    return 2
  fi
  sha256sum "$@"
  r=$?
  if [ "$r" -ne 0 ]; then
    sb_return_fail "$r" "sha256_failed"
    echo "SB_OP=fs.sha256" >&2
    return "$r"
  fi
  sb_return_ok
  echo "SB_OP=fs.sha256"
  return 0
}
