"""PHP parser v0: lists the functions in a PHP program, their parameters, which other
functions they call, and which risky built-ins they use. Output is JSON for the UI
dependency view. It is a lightweight text parser, not a full PHP parser: class methods
are listed like plain functions and calls through objects (->) are ignored.

Usage:
    python tools/parse_php.py datasets/dev/04_payroll
    python tools/parse_php.py datasets/dev/04_payroll --out results/parser/04_payroll.json
"""
import argparse
import json
import re
from pathlib import Path

KEYWORDS = {
    "if", "else", "elseif", "for", "foreach", "while", "do", "switch", "case", "catch", "try",
    "finally", "function", "fn", "return", "echo", "print", "array", "list", "isset", "empty",
    "unset", "exit", "die", "new", "match", "use", "declare", "include", "include_once",
    "require", "require_once", "and", "or", "xor", "self", "parent", "static", "clone", "throw",
}
# Calls worth a human look. This is NOT a vulnerability finding, only a pointer.
RISKY = {
    "eval", "exec", "shell_exec", "system", "passthru", "popen", "proc_open", "unserialize",
    "assert", "create_function", "extract", "mysql_query", "mysqli_query", "file_put_contents",
    "unlink", "move_uploaded_file", "header", "setcookie", "md5", "sha1", "rand", "mt_rand",
}

_TOKEN = re.compile(r"//[^\n]*|#[^\n]*|/\*.*?\*/|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", re.S)
_FUNC = re.compile(r"\bfunction\s+&?\s*([A-Za-z_]\w*)\s*\(")
_CALL = re.compile(r"(?<![\w$>:\\])([A-Za-z_]\w*)\s*\(")
_INCLUDE = re.compile(
    r"\b(?:require_once|include_once|require|include)\b\s*\(?\s*(?:__DIR__\s*\.\s*)?['\"]([^'\"]+)['\"]"
)


def _php_only(src):
    if "<?" not in src:
        return src
    return "\n".join(re.findall(r"<\?(?:php|=)?(.*?)(?:\?>|\Z)", src, re.S))


def _strip(src, blank_strings):
    """Remove comments; optionally blank out string contents so braces and
    parentheses inside strings cannot confuse the matching."""
    def repl(m):
        t = m.group(0)
        if t[0] in "/#":
            return " "
        return '""' if blank_strings else t
    return _TOKEN.sub(repl, src)


def _balanced(code, start, open_ch, close_ch):
    """Index just after the bracket that closes the one at code[start - 1]."""
    depth, i = 1, start
    while i < len(code) and depth:
        if code[i] == open_ch:
            depth += 1
        elif code[i] == close_ch:
            depth -= 1
        i += 1
    return i


def _find_functions(code):
    found = []
    for m in _FUNC.finditer(code):
        after_params = _balanced(code, m.end(), "(", ")")
        params = re.findall(r"\$\w+", code[m.end():after_params - 1])
        k = after_params
        while k < len(code) and code[k] not in "{;":
            k += 1
        if k >= len(code) or code[k] == ";":
            body = ""  # abstract or interface method
        else:
            body = code[k + 1:_balanced(code, k + 1, "{", "}") - 1]
        found.append({"name": m.group(1), "params": params, "body": body})
    return found


def parse_sources(sources, name="program"):
    """sources: {file name: php text}. Returns a JSON-ready dict."""
    parsed = {}
    for fname, text in sorted(sources.items()):
        php = _php_only(text)
        parsed[fname] = (
            _find_functions(_strip(php, True)),
            _INCLUDE.findall(_strip(php, False)),
        )
    defined = {}
    for funcs, _ in parsed.values():
        for f in funcs:
            defined.setdefault(f["name"].lower(), f["name"])

    functions, edges, files, warnings = [], [], [], []
    seen = set()
    for fname, (funcs, includes) in parsed.items():
        files.append({"file": fname, "functions": [f["name"] for f in funcs], "includes": includes})
        for f in funcs:
            if f["name"].lower() in seen:
                warnings.append(f"function {f['name']} is defined more than once")
            seen.add(f["name"].lower())
            body = re.sub(r"\bnew\s+[\w\\]+", " ", f["body"])
            calls, external, risky = set(), set(), set()
            for c in _CALL.findall(body):
                low = c.lower()
                if low in KEYWORDS:
                    continue
                if low in defined:
                    calls.add(defined[low])
                else:
                    external.add(c)
                    if low in RISKY:
                        risky.add(c)
            functions.append({
                "name": f["name"], "file": fname, "params": f["params"],
                "calls": sorted(calls), "external_calls": sorted(external),
                "risky_calls": sorted(risky),
            })
            edges += [{"from": f["name"], "to": c} for c in sorted(calls)]
    return {"program": name, "files": files, "functions": functions, "edges": edges,
            "warnings": warnings}


def parse_path(path):
    path = Path(path)
    if path.is_dir():
        sources = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in sorted(path.glob("*.php"))}
        return parse_sources(sources, path.name)
    return parse_sources({path.name: path.read_text(encoding="utf-8", errors="replace")}, path.stem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="a .php file or a program folder")
    ap.add_argument("--out", help="write JSON here instead of printing")
    args = ap.parse_args()
    text = json.dumps(parse_path(args.path), indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print("wrote", args.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
