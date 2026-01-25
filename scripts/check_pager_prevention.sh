#!/bin/bash

# HEE Pager Prevention Check Script
# External script to avoid YAML parsing issues and code exposure

echo "🔍 Checking for pager prevention in shell commands..."

# Find all git log commands without pager prevention
violations=$(grep -r "git log" --include="*.md" --include="*.sh" --include="*.yml" --include="*.yaml" . 2>/dev/null | grep -v "git --no-pager\|GIT_PAGER=cat" | grep -v "pager prevention" | head -5)

if [ -n "$violations" ]; then
    echo "❌ Found git log without pager prevention:"
    echo "$violations" | head -3
    exit 1
else
    echo "✅ Pager prevention check passed"
    exit 0
fi
