# cards.no-diff.shfn.bash
# stage: ~/.hee/library/bash/
# tiny shfn + selftest
# no set -e/-u/pipefail

card_red_no_diff() {
  out="$1"
  mkdir -p "$(dirname "$out")"
  cat > "$out" <<'CARD'
# RED CARD

Event: emitted diff/patch + expanded P0 surface
Ruling: violation

SB_CARD_KIND=red_card
SB_TOPIC=no_diff_no_patch_workflow
SB_TOPIC_2=no_extra_subcommands_p0
SB_ACTION=stop_and_correct
CARD
  rc=$?
  echo "card_red_no_diff.out=$out"
  echo "card_red_no_diff.rc=$rc"
  return "$rc"
}

card_pm_no_diff() {
  out="$1"
  mkdir -p "$(dirname "$out")"
  cat > "$out" <<'CARD'
# POSTMORTEM

What: diff/patch + P0 scope creep
Fix: no diffs here; keep P0 minimal

PM_TOPIC=no_diff_no_patch_workflow
PM_TOPIC_2=no_extra_subcommands_p0
PM_STATUS=recorded
CARD
  rc=$?
  echo "card_pm_no_diff.out=$out"
  echo "card_pm_no_diff.rc=$rc"
  return "$rc"
}

cards_no_diff_selftest() {
  cards_dir="$1"
  rc_path="$cards_dir/red-card-no-diff-and-no-extra-subcommands.md"
  pm_path="$cards_dir/PM-no-diff-and-no-extra-subcommands.card.md"

  card_red_no_diff "$rc_path"
  r1=$?
  card_pm_no_diff "$pm_path"
  r2=$?

  sha256sum "$rc_path" "$pm_path"
  r3=$?

  echo "selftest.cards_dir=$cards_dir"
  echo "selftest.red_path=$rc_path"
  echo "selftest.pm_path=$pm_path"
  echo "selftest.rc_red=$r1"
  echo "selftest.rc_pm=$r2"
  echo "selftest.rc_sha256=$r3"

  if [ "$r1" -eq 0 ] && [ "$r2" -eq 0 ] && [ "$r3" -eq 0 ]; then
    echo "selftest.status=ok"
    return 0
  fi

  echo "selftest.status=fail"
  return 1
}
