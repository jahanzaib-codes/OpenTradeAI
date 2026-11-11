# 🤝 Contributing to OpenTradeAI

Thank you for your interest in contributing to **OpenTradeAI**! We welcome contributions from quant researchers, software engineers, and machine learning practitioners.

## 📋 Code of Conduct
We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone. Please be respectful and professional in all interactions.

## 🛠️ Development Setup
1. **Fork and Clone:**
   ```bash
   git clone https://github.com/<your-username>/OpenTradeAI.git
   cd OpenTradeAI
   ```
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Branching Model:**
   * Create feature branches off `main`: `feature/your-feature-name`
   * Bug fixes: `fix/issue-description`
   * Performance optimizations: `perf/optimization-target`

## 📏 Code Style Guidelines
* Follow **PEP 8** style conventions.
* Provide clear docstrings for all classes, methods, and public functions.
* Include type annotations (`typing.Dict`, `typing.List`, `typing.Optional`, etc.) where appropriate.
* Ensure code passes flake8 linting (`flake8 . --count --select=E9,F63,F7,F82`).

## 🚀 Pull Request Process
1. Ensure all syntax checks pass before submitting your PR.
2. Update technical documentation in `README.md` and document user-facing changes in `CHANGELOG.md`.
3. Submit your PR against the `main` branch with a clear description of the problem solved.
