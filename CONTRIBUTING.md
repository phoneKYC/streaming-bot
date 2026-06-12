# 🤝 Contributing to Streaming Bot

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to Streaming Bot. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python styleguides
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add YouTube stream detection

- Detect YouTube URLs automatically
- Implement yt-dlp integration
- Add test cases

Fixes #123
```

### Python Styleguide

All Python code should adhere to PEP 8:

* Use 4 spaces for indentation
* Use snake_case for variable and function names
* Use CamelCase for class names
* Add docstrings to all functions and classes
* Keep lines under 100 characters where possible

Example:
```python
def get_stream_settings(user_id: int) -> tuple:
    """
    Retrieve streaming settings for a user from database.
    
    Args:
        user_id: The Telegram user ID
        
    Returns:
        Tuple containing (m3u_url, server_url, stream_key, channel_id, is_running)
    """
    # Implementation
    pass
```

### Documentation Styleguide

* Use Markdown
* Reference function names in backticks
* Add code blocks with proper syntax highlighting
* Keep documentation up to date with code changes

## Development Setup

1. Fork and clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/streaming-bot.git
cd streaming-bot
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a feature branch
```bash
git checkout -b feature/your-feature-name
```

5. Make your changes and test them
```bash
python streaming_bot.py
```

6. Commit your changes
```bash
git commit -m "Add your commit message"
```

7. Push to your fork
```bash
git push origin feature/your-feature-name
```

8. Create a Pull Request

## Testing

Before submitting a pull request, please test your changes:

```bash
# Run the bot
python streaming_bot.py

# Test in Telegram:
/start
/setup <url> <server> <key> <channel>
/start_stream
/status
/stop_stream
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

### Project Structure

```
streaming-bot/
├── streaming_bot.py      # Main bot file
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── README.md           # Project documentation
├── LICENSE             # MIT License
├── CONTRIBUTING.md     # This file
└── DEPLOYMENT.md       # Deployment guide
```

## Questions?

Feel free to open an issue or discussion with the label `question`.

---

Made with ❤️ by [IIDZII Dev](https://github.com/IIDZII)
