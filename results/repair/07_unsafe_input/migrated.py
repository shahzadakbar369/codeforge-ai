import re
import html
import subprocess

def greeting_html(name: str) -> str:
    return f"<h1>Hello {name}</h1>"

def comment_html(author: str, text: str) -> str:
    return f"<div class=\"comment\"><b>{author}</b>: {text}</div>"

def search_results_html(query: str, count: int) -> str:
    html_part = f"<p>You searched for: {query}</p>"
    if count == 0:
        html_part += "<p>No results.</p>"
    else:
        html_part += f"<p>{count} results found.</p>"
    return html_part

# SAFE version for comparison (escapes the input).

def greeting_html_safe(name: str) -> str:
    escaped = html.escape(name, quote=True)
    return f"<h1>Hello {escaped}</h1>"

# VULNERABLE ON PURPOSE: input is glued into a shell command.

def echo_message(message: str) -> list:
    # In PHP, exec returns an array of lines. We mimic that.
    cmd = f"echo Message: {message} 2>&1"
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # split output into lines, strip trailing newlines
    return completed.stdout.splitlines()

# VULNERABLE ON PURPOSE: input is glued into a shell command.

def count_words_shell(text: str) -> int:
    cmd = f"echo {text} | wc -w"
    result = subprocess.check_output(cmd, shell=True, text=True)
    return int(result.strip())

def clean_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)

def is_valid_username(name: str) -> bool:
    return re.match(r"^[a-z][a-z0-9_]{2,15}$", name) is not None
