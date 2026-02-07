#!/usr/bin/env bash
# hee_color.sh — canonical color/tty forcing helpers for evidence/tee workflows

# Default ON unless explicitly disabled.
: "${HEE_COLOR:=1}"

hee_color_env_export() {
  # Force color for common ecosystems.
  export FORCE_COLOR=1
  export CLICOLOR_FORCE=1
  export GH_FORCE_TTY=1

  # Respect explicit opt-out.
  if [[ "${HEE_COLOR}" == "0" ]]; then
    export FORCE_COLOR=0
    export CLICOLOR_FORCE=0
    unset GH_FORCE_TTY || true
  fi
}

hee_color_on()  { export HEE_COLOR=1; hee_color_env_export; }
hee_color_off() { export HEE_COLOR=0; hee_color_env_export; }

hee_color_status() {
  printf 'HEE_COLOR=%s\n' "${HEE_COLOR}"
  printf 'FORCE_COLOR=%s\n' "${FORCE_COLOR:-}"
  printf 'CLICOLOR_FORCE=%s\n' "${CLICOLOR_FORCE:-}"
  printf 'GH_FORCE_TTY=%s\n' "${GH_FORCE_TTY:-}"
}

hee_color_hint() {
  cat <<'EOF'
hee-color hints:
- When piping to tee, many CLIs disable color if stdout is not a TTY.
- Use: export GH_FORCE_TTY=1 FORCE_COLOR=1 CLICOLOR_FORCE=1
- For rg:   rg --color=always ...
- For git:  git -c color.ui=always ...
EOF
}
