# Contributing to Transcribe

Thank you for your interest in contributing to Transcribe!

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- FFmpeg

### Clone and Install

```bash
git clone https://github.com/piersrobcoleman/video-transcriber.git
cd video-transcriber
pip install -r requirements.txt
```

### Configuration

```bash
cp config.json.example config.json
# Edit config.json with your settings
```

See [Configuration Reference](docs/configuration.md) for all options.

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function signatures
- Maximum line length: 100 characters

### Formatting

We recommend using [Black](https://github.com/psf/black) for consistent formatting:

```bash
pip install black
black .
```

### Linting

We recommend [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
pip install ruff
ruff check .
```

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for custom output directory

- Add output_dir config option
- Update CLI to accept --output flag
- Update documentation
```

### Testing

Before submitting:

1. Test your changes with a sample video
2. Verify CLI options work as expected
3. Check that existing functionality still works

```bash
# Test basic transcription
python transcribe_video.py "test.mp4" --no-diarize

# Test with speaker ID
python transcribe_video.py "test.mp4"

# Test frame extraction
python extract_frames.py "test.mp4" --no-smart
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are tested and working
- [ ] Documentation updated if needed
- [ ] Commit messages are clear

## Reporting Issues

### Bug Reports

Use the [bug report template](../../issues/new?template=bug_report.md) and include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (full traceback)

### Feature Requests

Use the [feature request template](../../issues/new?template=feature_request.md) and describe:

- The problem you're trying to solve
- Your proposed solution
- Alternative approaches considered

## Questions?

- Check [existing issues](../../issues) first
- Open a [new issue](../../issues/new) for questions

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
