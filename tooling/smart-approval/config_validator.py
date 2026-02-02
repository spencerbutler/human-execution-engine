#!/usr/bin/env python3
"""
Configuration Validator for Smart Approval Safety Profiles
Schema-validates safety_profiles.yml and fails closed on invalid config.
"""

import yaml
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Schema for safety_profiles.yml
SAFETY_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "command_safety_profiles": {
            "type": "object",
            "properties": {
                "version": {"type": "number"},
                "profiles": {
                    "type": "object",
                    "properties": {
                        "read_only": {
                            "type": "object",
                            "properties": {
                                "allowlist_prefixes": {"type": "array", "items": {"type": "string"}},
                                "allowlist_exact": {"type": "array", "items": {"type": "string"}},
                                "denylist_contains": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["allowlist_prefixes", "allowlist_exact", "denylist_contains"]
                        },
                        "low_risk": {
                            "type": "object",
                            "properties": {
                                "allowlist_prefixes": {"type": "array", "items": {"type": "string"}},
                                "allowlist_exact": {"type": "array", "items": {"type": "string"}},
                                "denylist_contains": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["allowlist_prefixes", "allowlist_exact", "denylist_contains"]
                        }
                    },
                    "required": ["read_only", "low_risk"]
                },
                "decision_rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rule": {"type": "string"},
                            "action": {"type": "string"}
                        },
                        "required": ["rule", "action"]
                    }
                }
            },
            "required": ["version", "profiles", "decision_rules"]
        }
    },
    "required": ["command_safety_profiles"]
}

def validate_config(config_path):
    """Validate safety profiles configuration"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        validate(instance=config, schema=SAFETY_PROFILE_SCHEMA)

        # Additional semantic validation
        profiles = config["command_safety_profiles"]["profiles"]

        # Ensure no overlap between allowlists and denylists
        for profile_name, profile in profiles.items():
            allowlist = set(profile.get("allowlist_prefixes", []) + profile.get("allowlist_exact", []))
            denylist = set(profile.get("denylist_contains", []))

            overlap = allowlist & denylist
            if overlap:
                raise ValidationError(f"Profile {profile_name} has overlap between allowlist and denylist: {overlap}")

        return True, "Configuration is valid"

    except FileNotFoundError:
        return False, f"Configuration file not found: {config_path}"
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except ValidationError as e:
        return False, f"Schema validation error: {e.message}"

if __name__ == "__main__":
    config_path = Path(__file__).parent / "safety_profiles.yml"
    valid, message = validate_config(config_path)

    if valid:
        print("✅ Configuration validation passed")
        sys.exit(0)
    else:
        print(f"❌ Configuration validation failed: {message}")
        sys.exit(1)
