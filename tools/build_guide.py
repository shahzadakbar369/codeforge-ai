"""Build the concise team guide using ReportLab (authoring dependency only)."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

OUT = Path('output/pdf/CodeForge_AI_Guide.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)
S = getSampleStyleSheet()
S.add(ParagraphStyle(name='Body',fontName='Helvetica',fontSize=9.5,leading=14,textColor=colors.HexColor('#344c43'),spaceAfter=7))
S.add(ParagraphStyle(name='SmallText',parent=S['Body'],fontSize=8.2,leading=11,spaceAfter=5))
S.add(ParagraphStyle(name='Section',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=colors.HexColor('#315442'),spaceBefore=9,spaceAfter=7))
S.add(ParagraphStyle(name='Title2',fontName='Helvetica-Bold',fontSize=27,leading=32,textColor=colors.HexColor('#203e32'),spaceAfter=11))
S.add(ParagraphStyle(name='CodeBox',fontName='Courier',fontSize=7.6,leading=11,textColor=colors.HexColor('#244a38'),backColor=colors.HexColor('#f0f4ed'),borderPadding=9,spaceBefore=5,spaceAfter=10))
story=[]
def p(t,style='Body'): story.append(Paragraph(t,S[style]))
def h(t): p(t,'Section')
def code(t): story.append(Preformatted(t,S['CodeBox']))
def table(rows,widths):
    values=[[Paragraph(escape(str(v)),S['SmallText']) for v in row] for row in rows]
    t=Table(values,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8efdf')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dce5d5'))]))
    story.append(t);story.append(Spacer(1,7))
def page(k,title):
    if story: story.append(PageBreak())
    p(f'CODEFORGE AI / FIELD GUIDE / {k:02d}','SmallText');p(title,'Title2')
def flow():
    d=Drawing(498,220)
    def box(x,y,w,top,bottom):
        d.add(Rect(x,y,w,43,rx=7,fillColor=colors.HexColor('#eff4e9'),strokeColor=colors.HexColor('#cbd9bd')))
        d.add(String(x+w/2,y+26,top,textAnchor='middle',fontName='Helvetica-Bold',fontSize=9,fillColor=colors.HexColor('#315442')))
        d.add(String(x+w/2,y+12,bottom,textAnchor='middle',fontName='Helvetica',fontSize=7.2,fillColor=colors.HexColor('#65795a')))
    def arrow(x1,y1,x2,y2):
        d.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#8da678')))
        if y1==y2: d.add(Polygon([x2,y2,x2-5,y2+3,x2-5,y2-3],fillColor=colors.HexColor('#8da678'),strokeColor=None))
        else:d.add(Polygon([x2,y2,x2-3,y2+5,x2+3,y2+5],fillColor=colors.HexColor('#8da678'),strokeColor=None))
    box(0,166,145,'React studio','Code / files / ZIP / GitHub');box(178,166,145,'FastAPI job API','Validate, persist, enqueue');box(354,166,144,'Groq API','Translate / cases / repair')
    arrow(145,187,178,187);arrow(323,187,354,187)
    d.add(String(250,145,'Background worker: four sequential stages',fontName='Helvetica',fontSize=8,textAnchor='middle',fillColor=colors.HexColor('#65795a')))
    names=[('Parser','PHP AST + graph'),('Security','Potential source risks'),('Migration','Per-source Python modules'),('Test + repair','PHP vs Python returns')]
    for i,(a,b) in enumerate(names):
        box(i*128,83,114,a,b)
        if i<3:arrow(i*128+114,104,(i+1)*128,104)
    arrow(441,83,441,59)
    box(280,6,218,'Docker: PHP 8.3 / Python 3.12','Network off, read-only mount, resource limits')
    box(0,6,245,'Report + generated FastAPI project','JSON verdicts / source / Python / ZIP download')
    arrow(280,27,245,27)
    return d

page(1,'PHP to a reviewable\nPython project')
p('Team guide | Updated 23 November 2026','SmallText')
p('CodeForge AI is an AI-assisted React/FastAPI application. Four sequential specialist stages parse PHP, review potential source risks, translate each source file into Python, then compare sampled PHP/Python returns in Docker. It uses pretrained Groq inference; no model training is implemented.')
story.append(flow())
h('Team speaking responsibilities')
table([['Member','Lead area','Demonstrate'],['Shahzad','Orchestration, parsing, backend','Job lifecycle, PHP AST, module map, private history and failure handling.'],['Tahir','Security and testing','Source rules, PHP reference values, Docker isolation, comparison and repair.'],['Ayesha','React UI and CI/demo','Input modes, authentication/history, theme, evidence tabs and ZIP.']],[70,153,275])
p('All three share LLM integration and prompt design. These roles reflect team responsibility, not independent authorship of every new change. Review your files before presenting.','SmallText')
h('Opening statement')
p('"We migrate PHP into a reviewable Python/FastAPI project using four specialist stages. The output preserves file boundaries and includes a dependency map, security review and executed test evidence where supported."')

page(2,'Run and use the website')
h("After restarting Shahzad's laptop")
p('Start Docker Desktop and wait for its engine. Open VS Code in E:\\codeforge-ai. In PowerShell:')
code('cd E:\\codeforge-ai\npowershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\start_demo.ps1')
p('Open http://127.0.0.1:8001. Existing users sign in; new accounts need the invitation code printed in the terminal. Keep the terminal open; Ctrl+C stops it. Stop an old server before starting another. A single-process lock prevents duplicate backends sharing the same database.','SmallText')
h('Use it')
p('Choose pasted PHP, files/folder, ZIP or public GitHub URL. Mixed-language repositories are accepted; only PHP files are imported. Start migration, inspect Output / Graph / Security / Tests, select Python modules, review limits, and download the project ZIP. Use the built-in example or demo/presentation-php for rehearsal.','SmallText')
h('First setup or teammate update')
p('For a clean existing clone after Shahzad pushes:','SmallText')
code('git status\ngit switch develop\ngit pull --ff-only origin develop\n.\\.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt\nnpm --prefix frontend/react-app ci\nnpm --prefix frontend/react-app run build\ndocker pull php:8.3-cli\ndocker pull python:3.12-slim')
p('If .venv is missing: python -m venv .venv. If .env is missing, copy .env.example and add your own GROQ_API_KEY. Do not overwrite existing secrets or discard local Git changes. The backend environment takes precedence over .env. Never put keys in React or Git.','SmallText')
h('Optional free HTTPS demo link')
code('powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\share_demo.ps1')
p('Run in a second terminal. Share the printed trycloudflare.com URL and invitation code privately. Laptop, internet, Docker and both terminals must stay running. This is a temporary demo tunnel, not permanent hosting. The URL changes when restarted.','SmallText')

page(3,'Architecture and traceability')
h('How does it preserve system design?')
p('Each PHP source maps to a separate Python module: lib/add.php becomes converted/lib/add.py. A dependency plan orders translation and reports cycles. Relevant symbols and module names guide prompts. Static checks compare source definitions and expected imports with generated Python. The Graph tab exposes missing symbols/imports and unresolved dependencies.','SmallText')
p('<b>Say:</b> We retain file boundaries and provide structural traceability; static checks do not prove complete architecture or behavioral equivalence. Frameworks, inheritance and dynamic dispatch require review.','SmallText')
h('Storage schema')
code('users(id PK, email UNIQUE, salt, password [PBKDF2 hash])\nsessions(token_hash PK, user_id, csrf, expires)\njobs(id PK, user_id, created, label)\nattempts(client_key, at)\n\nusers 1 -> many sessions; users 1 -> many jobs\nSQLite: data/accounts.sqlite3; WAL mode\nJob files: data/jobs/{job_id}/')
h('Request lifecycle and artifacts')
p('Authenticate and validate -> reserve bounded capacity -> save source/ownership -> worker stages -> static checks -> report and ZIP. Defaults: two workers, twelve total pending/running jobs, two/account. Saturation returns 429 and Retry-After. Browser polling is lightweight and non-overlapping; queued jobs poll more slowly.','SmallText')
code('source/          original PHP\nstatus.json      full state, modules and report\nprogress.json    lightweight state/events\nconverted/       Python packages for verification\nproject/         app.py + registry.json + modules + source + tests\nproject.zip      downloaded project')
p('SQLite owns accounts, expiring sessions and job metadata; reports and artifacts are files. Passwords and session tokens are hashed. Cookies are HttpOnly, SameSite Strict and Secure over HTTPS. Mutations check CSRF and origin; history/report/download check job ownership.','SmallText')
h('Restarts')
p('Unfinished jobs become failed with an explicit restart message; partial outputs remain. A new job may reuse exact-source, same-owner checkpoints with matching module map and pipeline/model fingerprint. No automatic distributed resume is claimed. Archive old data manually; low disk space blocks new jobs.','SmallText')

page(4,'Security and validation')
h('Important fixes in this release')
table([['Problem','Implemented response'],['Unlimited backlog','Bounded global/account job admission; 429 + Retry-After; bounded API/upload/login concurrency.'],['Unsafe upload paths','Reject traversal, control characters, reserved Windows names, case collisions and module-name collisions before saving.'],['Failed submission artifacts','Rollback newly allocated job files, ownership and admission slot.'],['Request/polling overhead','Authentication off the event loop; SQLite WAL/schema initialization; summary polling and backoff.'],['Weak scanner evidence','AST-filtered patterns exclude comments/strings; variable calls request manual review.'],['Docker output/timeout risk','Bounded output buffers, time/resource limits and explicit named-container cleanup.'],['Restart/stale translations','Retain interrupted evidence; pipeline/model fingerprint prevents outdated reuse.']],[130,368])
h('What tests mean')
p('The LLM proposes inputs, not expected outputs. PHP runs twice to notice unstable reference returns. Python receives the same inputs; successful returned values are compared. Mismatches permit at most two repairs. EQUIVALENT applies only to executed cases; the same repair cases are not independent grading. Classes and full HTTP/side-effect behavior remain outside automatic verification.','SmallText')
p('A completed job means packaged output, not universal correctness. UNTESTED, UNTESTABLE, ERROR and MISMATCH remain visible. Decimal results project to JSON numbers; unsupported returns are isolated per case. Model JSON and invalid test-target responses receive bounded corrective retries. The scanner is not taint analysis or a full OWASP audit. Docker is defense in depth, not a guarantee against every malicious program.','SmallText')
h('Verification evidence')
p('32 backend tests and the React build passed. The controlled Docker fixture passed ten cases across three modules. Separate live Groq testing matched 70 of 72 cases, with two large-integer mismatches retained. This is not an accuracy benchmark. Consult docs/evidence/*2026-11-23.json for scope and outcomes. Load fixtures disable external inference/execution; thousands of fixture accounts are not thousands of real AI migrations. See PROGRESS.md for the final check count and limits.','SmallText')

page(5,'Presentation and team messages')
h('Tahir: ready-to-send preparation')
p('Please lead security and test generation. Review backend/agents.py and test_hardening.py. Explain AST-filtered heuristic source rules, potential versus confirmed findings, and manual review for dynamic calls. Show Security and Tests. The LLM proposes inputs; real PHP supplies reference returns; Python runs the same inputs, with at most two repairs. Explain Docker networking, mounts, privileges, resource/time/output limits and cleanup. UNTESTED is not a passing result. Keep older Semgrep/Bandit experiments separate from this web scanner. Pull develop after Shahzad pushes and rehearse one migration. We all share LLM integration work.','SmallText')
h('Ayesha: ready-to-send preparation')
p('Please lead React UI and CI/demo delivery. Review App.jsx, AuthPanel.jsx and ci.yml. Show login/private history, inputs, theme, stage events, module selector, reports and ZIP download. Explain lightweight non-overlapping polling and clear input/provider/queue errors. CI tests/builds and uploads React output; it does not deploy automatically. Only claim remote CI success after viewing a real Actions run. The free link is a laptop-backed tunnel. Pull after Shahzad pushes and rehearse the full flow. We all share LLM integration work.','SmallText')
h('Three-minute demo')
table([['Speaker','Show and say'],['Ayesha / 30 sec','Login, input modes, dark mode, small three-file example.'],['Shahzad / 45 sec','Start job; explain queue, four stages, AST and module mapping.'],['Tahir / 60 sec','Security finding, PHP/Python evidence, Docker and repair limits.'],['Ayesha / 25 sec','Select three modules, history and ZIP download.'],['Shahzad / 20 sec','State limits and next steps. Keep a saved successful result as backup.']],[135,363])
h('Viva answers to remember')
p('<b>How do agents prove execution?</b> Events plus actual graph/findings/modules/cases, not icons alone. <b>Is the architecture preserved?</b> File mapping, symbol/import checks and dependency evidence support traceability; full preservation is not proven. <b>Did you train a model?</b> No, pretrained inference. <b>Can it serve thousands?</b> Admission is bounded; the local load test does not establish production capacity.','SmallText')
h('Hosting and next work')
p('Vercel supports React and FastAPI, but the current persistent SQLite/files, single-process worker and Docker-daemon workflow need adaptation for serverless hosting. Render free storage is ephemeral. For this presentation, use the local app plus a temporary Cloudflare HTTPS tunnel. Future work: persistent cloud worker host, durable queue, broader class/framework tests, independent grading and deeper security analysis.','SmallText')
p('Official sources: vercel.com/docs/frameworks/backend/fastapi; render.com/docs/free; developers.cloudflare.com/tunnel/get-started/quick-tunnels/. Current full commands and messages: docs/PRESENTATION_READY.md and docs/DEPLOYMENT.md.','SmallText')

def furniture(canvas,doc):
    canvas.setTitle('CodeForge AI - User Guide and Viva Notes')
    canvas.setAuthor('CodeForge AI team')
    canvas.setSubject('Local migration studio: user guide, architecture, schema and team handoff')
    canvas.setStrokeColor(colors.HexColor('#d9e2d1'));canvas.line(48,43,547,43)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#829474'))
    canvas.drawString(48,29,'CODEFORGE AI  /  TEAM GUIDE  /  2026-11-23')
    canvas.drawRightString(547,29,str(doc.page))

SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=57).build(story,onFirstPage=furniture,onLaterPages=furniture)
print(OUT.resolve())
