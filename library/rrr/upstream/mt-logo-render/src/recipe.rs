//! Recipe data models and canonicalization logic.

use crate::{Error, Result};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use std::str::FromStr;

/// Base recipe specification for logo generation.
#[derive(Deserialize, Serialize, Clone, Debug, PartialEq)]
#[allow(dead_code)]
pub struct Recipe {
    /// Shape type for rendering
    pub shape: Shape,

    /// Output dimensions in pixels (WxH)
    pub size: Size,

    /// Primary fill color
    pub base_color: Color,

    /// Secondary color for patterns
    #[serde(skip_serializing_if = "Option::is_none")]
    pub accent_color: Option<Color>,

    /// Fill pattern specification
    #[serde(default)]
    pub fill: Fill,

    /// Overlay mark (check, x, dot)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mark: Option<Mark>,

    /// Corner badge indicator
    #[serde(skip_serializing_if = "Option::is_none")]
    pub badge: Option<Badge>,

    /// ASCII label text (1-4 chars recommended)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub label: Option<String>,

    /// Unicode glyph string
    #[serde(skip_serializing_if = "Option::is_none")]
    pub glyph: Option<String>,

    /// Filesystem path to font file
    #[serde(skip_serializing_if = "Option::is_none")]
    pub font_path: Option<PathBuf>,
}

/// Shape enumeration for logo rendering.
#[derive(Deserialize, Serialize, Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum Shape {
    Circle,
    Square,
    Triangle,
    Hex,
}

/// Size specification with width and height.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[allow(dead_code)]
pub struct Size {
    pub width: u32,
    pub height: u32,
}

impl Serialize for Size {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&format!("{}x{}", self.width, self.height))
    }
}

impl<'de> Deserialize<'de> for Size {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        s.parse().map_err(serde::de::Error::custom)
    }
}

impl FromStr for Size {
    type Err = String;

    fn from_str(s: &str) -> std::result::Result<Self, Self::Err> {
        let parts: Vec<&str> = s.split('x').collect();
        if parts.len() != 2 {
            return Err("Size must be in WxH format".to_string());
        }

        let width = parts[0].parse().map_err(|_| "Invalid width".to_string())?;
        let height = parts[1].parse().map_err(|_| "Invalid height".to_string())?;

        if width < 16 || height < 16 || width > 4096 || height > 4096 {
            return Err("Size must be between 16x16 and 4096x4096".to_string());
        }

        Ok(Size { width, height })
    }
}

/// Color representation supporting named and hex colors.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Color {
    Named(String),
    Hex(String),
}

impl Serialize for Color {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        match self {
            Color::Named(name) => serializer.serialize_str(name),
            Color::Hex(hex) => serializer.serialize_str(hex),
        }
    }
}

impl<'de> Deserialize<'de> for Color {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        s.parse().map_err(serde::de::Error::custom)
    }
}

impl FromStr for Color {
    type Err = String;

    fn from_str(s: &str) -> std::result::Result<Self, Self::Err> {
        if let Some(hex) = s.strip_prefix('#') {
            if hex.len() == 3 || hex.len() == 6 {
                for ch in hex.chars() {
                    if !ch.is_ascii_hexdigit() {
                        return Err("Invalid hex color".to_string());
                    }
                }
                Ok(Color::Hex(s.to_string()))
            } else {
                Err("Hex colors must be 3 or 6 digits".to_string())
            }
        } else if s
            .chars()
            .all(|c| c.is_alphanumeric() || c == '_' || c == '-')
        {
            Ok(Color::Named(s.to_string()))
        } else {
            Err("Invalid named color".to_string())
        }
    }
}

/// Fill pattern specifications.
#[derive(Deserialize, Serialize, Clone, Debug, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
#[derive(Default)]
pub enum Fill {
    #[default]
    Solid,
    Pie(u16),   // Degrees (circle only)
    Split(u8),  // Number of segments
    Stripe(u8), // Number of stripes
}

/// Overlay mark types.
#[derive(Deserialize, Serialize, Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum Mark {
    Check,
    X,
    Dot,
}

/// Corner badge types.
#[derive(Deserialize, Serialize, Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum Badge {
    CornerDot,
    CornerCheck,
}

/// Canonicalized recipe with normalized values.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize)]
#[allow(dead_code)]
pub struct CanonicalRecipe {
    pub shape: Shape,
    pub size: Size,
    pub base_color: String, // Normalized hex
    pub accent_color: Option<String>,
    pub fill: Fill,
    pub mark: Option<Mark>,
    pub badge: Option<Badge>,
    pub label: Option<String>, // Sanitized
    pub glyph: Option<String>,
    pub font_path: Option<PathBuf>,
}

/// Effective recipe with degradation notes.
#[allow(dead_code)]
pub struct EffectiveRecipe {
    pub requested: Recipe,
    pub effective: Recipe,
    pub notes: Vec<String>,
}

impl Recipe {
    /// Parse recipe from JSON string.
    pub fn from_json(json: &str) -> Result<Self> {
        serde_json::from_str(json).map_err(Error::Json)
    }

    /// Parse recipe from YAML string.
    pub fn from_yaml(yaml: &str) -> Result<Self> {
        serde_yaml::from_str(yaml).map_err(|e| Error::Validation(e.to_string()))
    }

    /// Validate recipe structure and constraints.
    pub fn validate(&self) -> Result<()> {
        // Size constraints
        if self.size.width < 16 || self.size.height < 16 {
            return Err(Error::Validation("Size must be at least 16x16".to_string()));
        }
        if self.size.width > 4096 || self.size.height > 4096 {
            return Err(Error::Validation(
                "Size must not exceed 4096x4096".to_string(),
            ));
        }

        // Label constraints
        if let Some(label) = &self.label {
            if label.is_empty() {
                return Err(Error::Validation("Label cannot be empty".to_string()));
            }
            if label.chars().count() > 4 {
                return Err(Error::Validation(
                    "Label must be 4 characters or less".to_string(),
                ));
            }
        }

        // Font path validation
        if let Some(path) = &self.font_path {
            if !path.exists() {
                return Err(Error::Validation(format!(
                    "Font path does not exist: {}",
                    path.display()
                )));
            }
        }

        Ok(())
    }

    /// Canonicalize recipe for deterministic processing.
    pub fn canonicalize(&self) -> Result<CanonicalRecipe> {
        let base_color = normalize_color(&self.base_color)?;
        let accent_color = self
            .accent_color
            .as_ref()
            .map(normalize_color)
            .transpose()?;
        let label = self.label.as_ref().and_then(|l| sanitize_label(l));

        Ok(CanonicalRecipe {
            shape: self.shape,
            size: self.size,
            base_color,
            accent_color,
            fill: self.fill.clone(),
            mark: self.mark,
            badge: self.badge,
            label,
            glyph: self.glyph.clone(),
            font_path: self.font_path.clone(),
        })
    }

    /// Generate deterministic stem from recipe.
    pub fn generate_stem(&self) -> Result<String> {
        let canonical = self.canonicalize()?;
        let recipe_id = generate_recipe_id(&canonical);
        let accent_token = canonical
            .accent_color
            .as_ref()
            .map(|c| format!("-{}", c))
            .unwrap_or_default();

        let tokens = generate_tokens(&canonical)?;
        let token_string = tokens.join("-");
        let size = format!("{}x{}", canonical.size.width, canonical.size.height);

        Ok(format!(
            "{}-{}-{}-{}-{}",
            recipe_id, canonical.base_color, accent_token, token_string, size
        ))
    }
}

/// Normalize color to lowercase hex format.
fn normalize_color(color: &Color) -> Result<String> {
    match color {
        Color::Named(name) => {
            // Convert named colors to hex
            match name.as_str() {
                "red" => Ok("ff0000".to_string()),
                "green" => Ok("00ff00".to_string()),
                "blue" => Ok("0000ff".to_string()),
                "black" => Ok("000000".to_string()),
                "white" => Ok("ffffff".to_string()),
                "yellow" => Ok("ffff00".to_string()),
                "cyan" => Ok("00ffff".to_string()),
                "magenta" => Ok("ff00ff".to_string()),
                "gray" | "grey" => Ok("808080".to_string()),
                _ => Err(Error::Validation(format!("Unknown color name: {}", name))),
            }
        }
        Color::Hex(hex) => {
            let hex = hex.strip_prefix('#').unwrap_or(hex);
            let hex = hex.to_lowercase();
            match hex.len() {
                3 => Ok(format!(
                    "{}{}{}{}{}{}",
                    &hex[0..1],
                    &hex[0..1],
                    &hex[1..2],
                    &hex[1..2],
                    &hex[2..3],
                    &hex[2..3]
                )),
                6 => Ok(hex),
                _ => Err(Error::Validation("Invalid hex length".to_string())),
            }
        }
    }
}

/// Sanitize label text for deterministic output.
fn sanitize_label(label: &str) -> Option<String> {
    let sanitized: String = label
        .chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '_' || *c == '.' || *c == '-')
        .take(4)
        .collect();

    if sanitized.is_empty() {
        None
    } else {
        Some(sanitized.to_uppercase())
    }
}

/// Generate deterministic recipe ID from canonical recipe.
fn generate_recipe_id(canonical: &CanonicalRecipe) -> String {
    let canonical_json = serde_json::to_string(canonical)
        .map_err(Error::Json)
        .unwrap(); // Should not fail for valid data

    let hash = Sha256::digest(canonical_json.as_bytes());
    let hash_bytes = hash.as_slice();
    format!(
        "recipe-{:x}",
        hash_bytes[0..8]
            .iter()
            .fold(0u64, |acc, &x| (acc << 8) | x as u64)
    )
}

/// Generate token list for stem creation.
fn generate_tokens(canonical: &CanonicalRecipe) -> Result<Vec<String>> {
    let mut tokens = Vec::new();

    // Fill token (always present)
    tokens.push(match &canonical.fill {
        Fill::Solid => "fill-solid".to_string(),
        Fill::Pie(degrees) => format!("fill-pie:{}", degrees),
        Fill::Split(segments) => format!("fill-split:{}", segments),
        Fill::Stripe(count) => format!("fill-stripe:{}", count),
    });

    // Mark token (always present)
    tokens.push(match canonical.mark {
        Some(Mark::Check) => "mark-check".to_string(),
        Some(Mark::X) => "mark-x".to_string(),
        Some(Mark::Dot) => "mark-dot".to_string(),
        None => "mark-none".to_string(),
    });

    // Badge token (always present)
    tokens.push(match canonical.badge {
        Some(Badge::CornerDot) => "badge-corner-dot".to_string(),
        Some(Badge::CornerCheck) => "badge-corner-check".to_string(),
        None => "badge-none".to_string(),
    });

    // Label token (only if present)
    if let Some(label) = &canonical.label {
        tokens.push(format!("label-{}", label.to_uppercase()));
    }

    // Glyph token (only if present and renderable)
    if let Some(glyph) = &canonical.glyph {
        let encoded = encode_unicode_glyph(glyph);
        tokens.push(format!("glyph-{}", encoded));
    }

    // Font token (only if external font used)
    if let Some(font_path) = &canonical.font_path {
        let hash = compute_font_hash(font_path)?;
        tokens.push(format!("font-{}", &hash[0..16])); // Take first 16 chars of hex string
    }

    Ok(tokens)
}

/// Encode Unicode glyph for deterministic tokens.
fn encode_unicode_glyph(glyph: &str) -> String {
    glyph
        .chars()
        .map(|c| format!("U{:08X}", c as u32))
        .collect::<Vec<_>>()
        .join("_")
}

/// Compute hash of font file for deterministic identification.
fn compute_font_hash(font_path: &Path) -> Result<String> {
    use std::fs;
    let content = fs::read(font_path)?;
    let hash = Sha256::digest(&content);
    let hash_bytes = hash.as_slice();
    Ok(format!(
        "{:x}",
        hash_bytes[0..8]
            .iter()
            .fold(0u64, |acc, &x| (acc << 8) | x as u64)
    ))
}

/// Resolve effective recipe with degradation logic.
pub fn resolve_effective_recipe(requested: &Recipe) -> EffectiveRecipe {
    let mut effective = requested.clone();
    let mut notes = Vec::new();

    // Validate and degrade fill patterns
    match (&requested.shape, &requested.fill) {
        (Shape::Circle, Fill::Pie(_)) => {
            // Pie fill is valid for circles
        }
        (_, Fill::Pie(_)) => {
            // Degrade to solid for other shapes
            effective.fill = Fill::Solid;
            notes.push("Pie fill only supported for circles, using solid".to_string());
        }
        (Shape::Hex, Fill::Split(n)) if *n == 2 || *n == 3 || *n == 6 => {
            // Valid split counts for hexagons
        }
        (_, Fill::Split(_)) => {
            // Degrade to solid
            effective.fill = Fill::Solid;
            notes.push("Unsupported split count for shape, using solid".to_string());
        }
        _ => {
            // Other fills are generally supported
        }
    }

    // Validate glyph rendering capability
    if let Some(glyph) = &requested.glyph {
        if requested.font_path.is_none() {
            // Check if glyph is ASCII-renderable with microfont
            if !is_ascii_only(glyph) {
                effective.glyph = None;
                notes.push("Unicode glyph requires font_path, omitted".to_string());
            }
        }
    }

    EffectiveRecipe {
        requested: requested.clone(),
        effective,
        notes,
    }
}

/// Check if string contains only ASCII characters.
fn is_ascii_only(s: &str) -> bool {
    s.is_ascii()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_size_parsing() {
        assert_eq!(
            "256x256".parse::<Size>().unwrap(),
            Size {
                width: 256,
                height: 256
            }
        );
        assert!("invalid".parse::<Size>().is_err());
        assert!("10x10".parse::<Size>().is_err()); // Too small
    }

    #[test]
    fn test_color_normalization() {
        assert_eq!(
            normalize_color(&Color::Named("red".to_string())).unwrap(),
            "ff0000"
        );
        assert_eq!(
            normalize_color(&Color::Hex("#ff0000".to_string())).unwrap(),
            "ff0000"
        );
        assert_eq!(
            normalize_color(&Color::Hex("#f00".to_string())).unwrap(),
            "ff0000"
        );
    }

    #[test]
    fn test_recipe_validation() {
        let valid_recipe = Recipe {
            shape: Shape::Circle,
            size: Size {
                width: 256,
                height: 256,
            },
            base_color: Color::Named("blue".to_string()),
            accent_color: None,
            fill: Fill::Solid,
            mark: None,
            badge: None,
            label: Some("TEST".to_string()),
            glyph: None,
            font_path: None,
        };
        assert!(valid_recipe.validate().is_ok());

        let invalid_recipe = Recipe {
            size: Size {
                width: 10,
                height: 10,
            }, // Too small
            ..valid_recipe
        };
        assert!(invalid_recipe.validate().is_err());
    }
}
