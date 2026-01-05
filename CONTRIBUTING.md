# Contributing to learn_language_through_novel

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## Commit Message Guidelines

We follow **Conventional Commits** format for clear, consistent commit history that can be automatically processed.

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies, config updates

### Rules

1. **Subject line** (first line):
   - Use imperative mood: "add" not "added" or "adds"
   - Don't capitalize the first letter
   - No period at the end
   - Max 50 characters

2. **Body** (optional):
   - Separate from subject with a blank line
   - Wrap at 72 characters
   - Explain **what** and **why**, not how
   - Use bullet points with `-` or `*` for multiple items

3. **Footer** (optional):
   - Reference issues: `Closes #123` or `Refs #123`
   - Breaking changes: `BREAKING CHANGE: description`

### Examples

#### Good Commits ✅

```
feat: add Piper TTS provider integration

- Implement PiperTTSProvider with voice model loading
- Add support for zh_CN, vi_VN, and en_US voices
- Generate 22050 Hz WAV output

Closes #45
```

```
fix: prevent duplicate prefixes in explanation segments

The TTS prefix was being added to every language-split segment
within explanations. Now only the first segment gets the prefix,
making the audio flow more naturally.
```

```
docs: update API documentation for /tts/synthesize endpoint
```

```
refactor: extract language detection into separate function
```

#### Bad Commits ❌

```
Fixed stuff
```
_Problem: Too vague, no context_

```
feat: Added new feature for TTS processing and also fixed some bugs in the audio system.
```
_Problem: Multiple changes in one commit, should be split_

```
Feature: Add support for OpenAI TTS.
```
_Problem: Capitalized, has period, wrong format_

---

## Setup Git Commit Template

To use the commit message template automatically:

```bash
git config --local commit.template .gitmessage
```

Now when you run `git commit`, your editor will open with the template.

---

## Development Workflow

1. **Set up your environment** (Python 3.12 required):
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes** with clear, atomic commits

4. **Test your changes**:
   ```bash
   python -m pytest tests/
   python scripts/generate.py tasks/task1.json
   ```

5. **Update documentation** if needed (CHANGELOG.md, docs/, README.md)

6. **Push and create a Pull Request**

---

## Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Keep functions focused and well-named
- Add docstrings for complex functions
- Comment the "why", not the "what"

---

## Testing

- Add tests for new features
- Ensure existing tests pass before submitting
- Test both success and error cases

---

## Questions?

Feel free to open an issue for discussion before starting major changes.
