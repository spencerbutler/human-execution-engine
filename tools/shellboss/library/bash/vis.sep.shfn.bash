# vis.sep.shfn.bash
# stage: ~/.hee/library/bash/
# PURPOSE: visual helpers (stdout only): separators + referee flags
#
# DOC (md-compat):
#   - . ~/.hee/library/bash/vis.sep.shfn.bash
#   - vis_sep [n] [ch] ["LABEL"]    -> rule (+ optional label)
#   - vis_flag <green|yellow|red> <msg>  -> colored emoji flag line
#
# COLOR:
#   - default: color ON when stdout is TTY
#   - VIS_COLOR=0 disables
#   - VIS_COLOR=1 enables (still TTY-gated)

vis__is_tty() { [ -t 1 ]; }

vis__color_ok() {
  case "${VIS_COLOR:-1}" in
    0|false|no) return 1 ;;
  esac
  vis__is_tty
}

vis__c() {
  # $1 = sgr code, $2 = text
  if vis__color_ok; then
    printf '\033[%sm%s\033[0m' "$1" "$2"
  else
    printf '%s' "$2"
  fi
}

vis_sep() {
  n="${1:-80}"
  ch="${2:--}"
  label="${3:-}"

  printf -v rule "%*s" "$n" ""
  rule="${rule// /$ch}"

  vis__c "36" "$rule"
  printf "\n"

  if [ -n "$label" ]; then
    vis__c "1;37" "$label"
    printf "\n"
    vis__c "36" "$rule"
    printf "\n"
  fi
}

vis_flag() {
  kind="${1:-}"
  shift || true
  msg="$*"

  case "$kind" in
    green)  emoji="🟢"; sgr="32" ;;
    yellow) emoji="🟡"; sgr="33" ;;
    red)    emoji="🟥"; sgr="31" ;;
    *)      emoji="⚪"; sgr="37" ;;
  esac

  if [ -z "$msg" ]; then msg="(no message)"; fi

  if vis__color_ok; then
    printf "%s " "$emoji"
    vis__c "1;$sgr" "$kind"
    printf " "
    vis__c "0" "$msg"
    printf "\n"
  else
    printf "%s %s %s\n" "$emoji" "$kind" "$msg"
  fi
}
