#!/bin/bash

# HEE Model Disclosure Check Script
# External script to avoid YAML parsing issues in pre-commit config

echo "Checking for model disclosure in current commit..."

# Get commit message file
commit_msg_file="${1:-.git/COMMIT_EDITMSG}"

# Extract commit message
if [ -f "$commit_msg_file" ]; then
    commit_msg=$(cat "$commit_msg_file" 2>/dev/null || echo "")
else
    commit_msg=$(git --no-pager log --format=%B -n 1 HEAD 2>/dev/null || echo "")
fi

# Check for model disclosure pattern
if echo "$commit_msg" | grep -q "\[model:[[:space:]]*[a-zA-Z0-9._-]\+"; then
    echo "Model disclosure found"
    exit 0
else
    echo "HEE Violation: Model disclosure required"
    echo "Format: [model: claude-3.5-sonnet] or [model: gpt-4]"
    echo "Add model disclosure to commit message"
    echo "Example: git commit -m 'feat: fix state capsule references [model: claude-3.5-sonnet]'"
    exit 1
fi
