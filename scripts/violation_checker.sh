#!/bin/bash

# HEE Violation Checker Script
# Pre-commit hook for automated violation detection and prevention

set -e

echo "🔍 HEE Violation Prevention Check"
echo "=================================="

VIOLATION_SCORE=0
VIOLATIONS_FOUND=()

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to add violation
add_violation() {
    local code="$1"
    local description="$2"
    local points="$3"
    local severity="$4"
    
    VIOLATION_SCORE=$((VIOLATION_SCORE + points))
    VIOLATIONS_FOUND+=("$code: $description ($points points - $severity)")
    echo -e "${RED}❌ $code: $description${NC}"
}

# Function to add warning
add_warning() {
    local code="$1"
    local description="$2"
    
    echo -e "${YELLOW}⚠️  $code: $description${NC}"
}

# Function to add success
add_success() {
    local message="$1"
    
    echo -e "${GREEN}✅ $message${NC}"
}

# Check 1: Branch Management
echo "📋 Checking Branch Management..."
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
    add_violation "BM-001" "Direct commit to main/master branch not allowed" 3 "Level 2"
elif [[ ! "$current_branch" =~ ^feature/ ]]; then
    add_violation "BM-004" "Branch name should follow feature/ pattern" 1 "Level 1"
else
    add_success "Branch management compliance"
fi

# Check 2: Model Disclosure
echo ""
echo "📋 Checking Model Disclosure..."
commit_msg=$(git log --format=%B -n 1 HEAD 2>/dev/null || echo "")
if [[ ! "$commit_msg" =~ \[model: ]]; then
    add_violation "CH-001" "Missing model disclosure in commit message" 1 "Level 1"
    add_warning "CH-001" "Include [model: <model-name>] in commit message"
else
    add_success "Model disclosure compliance"
fi

# Check 3: Working Directory
echo ""
echo "📋 Checking Working Directory..."
current_dir=$(pwd)
project_root=$(git rev-parse --show-toplevel)
if [[ "$current_dir" != "$project_root" ]]; then
    add_violation "WC-001" "Not working from project root directory" 7 "Level 4"
    add_warning "WC-001" "Current: $current_dir, Expected: $project_root"
else
    add_success "Working directory compliance"
fi

# Check 4: State Capsule Updates
echo ""
echo "📋 Checking State Capsule Updates..."
state_capsule_dir="$project_root/docs/STATE_CAPSULES"
if [[ -d "$state_capsule_dir" ]]; then
    # Check if state capsule was updated recently
    latest_capsule=$(find "$state_capsule_dir" -name "*.md" -type f -exec stat -c "%Y %n" {} \; 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    if [[ -n "$latest_capsule" ]]; then
        capsule_age=$(($(date +%s) - $(stat -c "%Y" "$latest_capsule" 2>/dev/null || echo 0)))
        if [[ $capsule_age -gt 86400 ]]; then # 24 hours
            add_violation "WC-002" "State capsule not updated recently" 7 "Level 4"
            add_warning "WC-002" "Update state capsule after significant operations"
        else
            add_success "State capsule compliance"
        fi
    else
        add_violation "WC-002" "No state capsule directory found" 7 "Level 4"
    fi
else
    add_violation "WC-002" "State capsule directory missing" 7 "Level 4"
fi

# Check 5: Documentation References
echo ""
echo "📋 Checking Documentation References..."
required_docs=("docs/HEE_POLICY.md" "docs/STATE_CAPSULE_GUIDE.md" "prompts/PROMPTING_RULES.md")
missing_docs=()

for doc in "${required_docs[@]}"; do
    if [[ ! -f "$project_root/$doc" ]]; then
        missing_docs+=("$doc")
    fi
done

if [[ ${#missing_docs[@]} -gt 0 ]]; then
    add_violation "PA-001" "Missing required documentation files" 1 "Level 1"
    for doc in "${missing_docs[@]}"; do
        add_warning "PA-001" "Missing: $doc"
    done
else
    add_success "Documentation compliance"
fi

# Check 6: Pre-commit Configuration
echo ""
echo "📋 Checking Pre-commit Configuration..."
if [[ -f "$project_root/.pre-commit-config.yaml" ]]; then
    if grep -q "hee-violation-check" "$project_root/.pre-commit-config.yaml"; then
        add_success "Pre-commit configuration compliance"
    else
        add_violation "WC-003" "HEE violation check not configured in pre-commit" 5 "Level 3"
    fi
else
    add_violation "WC-003" "Pre-commit configuration missing" 5 "Level 3"
fi

# Summary
echo ""
echo "📊 Violation Summary"
echo "==================="
echo "Total Violation Score: $VIOLATION_SCORE points"

if [[ $VIOLATION_SCORE -eq 0 ]]; then
    echo -e "${GREEN}🎉 Excellent compliance! No violations detected.${NC}"
    exit 0
elif [[ $VIOLATION_SCORE -le 5 ]]; then
    echo -e "${YELLOW}✅ Good compliance with minor issues.${NC}"
    exit 0
elif [[ $VIOLATION_SCORE -le 15 ]]; then
    echo -e "${YELLOW}⚠️  Fair compliance - improvement needed.${NC}"
    exit 1
elif [[ $VIOLATION_SCORE -le 30 ]]; then
    echo -e "${RED}❌ Poor compliance - immediate action required.${NC}"
    exit 1
else
    echo -e "${RED}🚨 Critical compliance failure - operations suspended.${NC}"
    exit 1
fi

# Print detailed violations
if [[ ${#VIOLATIONS_FOUND[@]} -gt 0 ]]; then
    echo ""
    echo "📋 Detailed Violations:"
    for violation in "${VIOLATIONS_FOUND[@]}"; do
        echo "  - $violation"
    done
fi

# Exit with appropriate code based on violation score
if [[ $VIOLATION_SCORE -ge 20 ]]; then
    echo ""
    echo -e "${RED}🚫 Commit blocked due to high violation score.${NC}"
    echo "Please address violations before committing."
    exit 1
elif [[ $VIOLATION_SCORE -ge 10 ]]; then
    echo ""
    echo -e "${YELLOW}⚠️  Commit allowed with violations. Review recommended.${NC}"
    exit 0
else
    echo ""
    echo -e "${GREEN}✅ Commit allowed.${NC}"
    exit 0
fi
