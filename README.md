# Human Execution Engine (HEE) & Runtime (HEER)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Canonical source of truth for Human Execution Engine standards**
>
> Defines HEE (conceptual model) and HEER (operational runtime) specifications
> for deterministic human work orchestration.

## 🏗️ Architecture Layers

### HEE (Human Execution Engine) - Conceptual Model
The normative definition of systems treating humans as constrained processing units.

### HEER (Human Execution Engine Runtime) - Operational Substrate
The enforcement layer defining state machines, scheduling semantics, and deterministic replay.

## 📚 Documentation

### 📋 **Core Specifications**
- [**🎯 HEE**](docs/HEE.md) - Canonical conceptual model specification
- [**⚙️ HEER**](docs/HEER.md) - Runtime contract and operational semantics
- [**📋 SPEC**](docs/SPEC.md) - Standards requirements and implementation criteria

### 🔒 **Security Foundation**
- [**🛡️ SECURITY**](docs/SECURITY.md) - Security requirements and threat model
- [**✅ Security Validator**](scripts/security_validator.py) - Input validation and compliance testing
- [**🔍 Security Scanner**](scripts/security_scanner.py) - Automated vulnerability scanning

### 🛠️ **Implementation & Standards**
- [**🗺️ Roadmap**](docs/ROADMAP.md) - 7-phase development plan with file trees
- [**📝 Development Guide**](prompts/PROMPTING_RULES.md) - Security-first development methodology
- [**🔧 Implementation Prompts**](prompts/) - Structured phase-by-phase guidance

## 🏃‍♂️ Quick Start

### For Standards Compliance
```bash
# Clone the canonical specifications
git clone git@github.com:spencerbutler/human-execution-engine.git
cd human-execution-engine

# Read the core specifications
cat docs/HEE.md    # Conceptual model
cat docs/HEER.md   # Runtime contract

# Follow the development roadmap
cat docs/ROADMAP.md
```

### For Implementation Guidance
```bash
# Start with foundational prompts
cat prompts/PROMPTING_RULES.md  # Development rules
cat prompts/00-specs-foundation.md  # Phase 1 guidance
```

## 🏗️ Ecosystem Integration

### Current Implementations
- [**tick-task**](https://github.com/spencerbutler/tick-task) - Task management with HEER runtime
- [**MT-logo-render**](https://github.com/spencerbutler/MT-logo-render) - Logo generation with HEE semantics

### Standards Compliance
This repository provides the **canonical specifications** that implementations must follow:

- **HEE Compliance**: 8 normative properties for human work orchestration
- **HEER Compliance**: Deterministic runtime with state machines and event journaling
- **Security Requirements**: Comprehensive validation and sanitization standards
- **Interoperability**: Standard APIs for ecosystem integration

## 🤝 Contributing

### Development Process
1. **📖 Read the Specs** - HEE.md and HEER.md are normative
2. **📝 Follow Prompts** - Use numbered prompts (00-06) for structured development
3. **🔒 Security First** - All changes validated against security requirements
4. **✅ Compliance** - New features must maintain specification compliance
5. **🧪 Testing** - Security validation before implementation

### Standards Evolution
- HEE/HEER specifications require consensus across ecosystem maintainers
- Breaking changes require migration guides and coordination
- Security changes require immediate ecosystem notification

## 📊 Project Status

### ✅ **Completed: Phase 1 (Specifications Foundation)**
- Canonical HEE and HEER specifications
- Complete development methodology (prompts 00-06)
- Comprehensive implementation roadmap
- Repository infrastructure and security foundations

### 🚧 **Next: Phase 2 (Architecture & API Design)**
Following `prompts/01-architecture-api.md` for core abstractions and API contracts.

## 📄 License

**MIT License** - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Market Thesis Ecosystem** - Integrated standards for human work orchestration
- **tick-task & MT-logo-render** - Reference implementations validating the standards
- **AI Development** - Claude, GPT, and other models contributing to HEE/HEER evolution

---

**Defining the future of human work orchestration** 🚀

## 📖 Technical Specifications

### Human Execution Engine (HEE)
A bounded, stateful execution system treating humans as primary runtime with deterministic orchestration. See [HEE Specification](docs/HEE.md) for complete normative definition.

### Human Execution Engine Runtime (HEER)
Deterministic execution runtime with state machines, event journaling, and admission control. See [HEER Specification](docs/HEER.md) for complete operational contract.

### Development Standards
Security-first development with numbered prompts ensuring consistent, high-quality implementation. See [Prompting Rules](prompts/PROMPTING_RULES.md) for enforcement guidelines.
