import os, subprocess, html

def t_sqli(db, x, name):
    # ruleid: codeforge-py-sqli-string-built
    db.execute("SELECT * FROM users WHERE name = '" + name + "'")
    q = f"DELETE FROM users WHERE id = {x}"
    # ruleid: codeforge-py-sqli-string-built
    db.execute(q)
    # ruleid: codeforge-py-sqli-string-built
    db.execute("SELECT * FROM t WHERE a = '%s'" % name)
    # ok: codeforge-py-sqli-string-built
    db.execute("SELECT * FROM users WHERE id = ?", (x,))
    # ok: codeforge-py-sqli-string-built
    db.execute("SELECT COUNT(*) FROM users")

def t_shell(x):
    # ruleid: codeforge-py-shell-call-with-variable
    os.system("ping -c 1 " + x)
    cmd = "echo " + x
    # ruleid: codeforge-py-shell-call-with-variable
    subprocess.check_output(cmd, shell=True, text=True)
    # ruleid: codeforge-py-shell-call-with-variable
    os.popen(cmd)
    # ok: codeforge-py-shell-call-with-variable
    subprocess.check_output("ls -l", shell=True)
    # ok: codeforge-py-shell-call-with-variable
    subprocess.run(["ls", x])

def t_html(name):
    # ruleid: codeforge-py-html-returned-unescaped
    return "<h1>Hello " + name + "</h1>"

def t_html2(name):
    # ruleid: codeforge-py-html-returned-unescaped
    return f"<h1>Hello {name}</h1>"

def t_html_ok(name):
    # ok: codeforge-py-html-returned-unescaped
    return "<h1>Hello " + html.escape(name) + "</h1>"

def t_html_ok2(name):
    # ok: codeforge-py-html-returned-unescaped
    return f"<h1>Hello {html.escape(name)}</h1>"
