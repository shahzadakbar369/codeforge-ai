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
    names=[('Parser','PHP AST + graph'),('Security','Potential source risks'),('Migration','Typed Python module'),('Test + repair','PHP vs Python returns')]
    for i,(a,b) in enumerate(names):
        box(i*128,83,114,a,b)
        if i<3:arrow(i*128+114,104,(i+1)*128,104)
    arrow(441,83,441,59)
    box(280,6,218,'Docker: PHP 8.3 / Python 3.12','Network off, read-only mount, resource limits')
    box(0,6,245,'Report + generated FastAPI project','JSON verdicts / source / Python / ZIP download')
    arrow(280,27,245,27)
    return d

page(1,'From legacy PHP\nto a reviewable Python project')
p('Local prototype | Team guide | 16 November 2026','SmallText')
p('CodeForge AI accepts PHP source, extracts structural dependencies, flags potential security risks, translates logic through Groq and compares real PHP returns with generated Python in Docker. The output is a Python module with a FastAPI function-call wrapper and an evidence report.')
story.append(flow())
h('Who owns each part in the presentation?')
table([['Member','Lead area','What to explain'],['Shahzad','Orchestration, parsing, backend','Ingestion, AST graph, stage order, job endpoints and storage.'],['Tahir','Security and test generation','Source risk rules, golden values, Docker, comparison and repair.'],['Ayesha','React UI and CI/demo','Input modes, dark mode, polling, report tabs, download and CI build.']],[70,153,275])
p('All three share LLM integration and prompt design. These are team-supplied presentation roles, not proof of individual authorship for every new line. Describe AI-assisted work accurately. No model training or fine-tuning is implemented.','SmallText')
h('What the word agent means here')
p('Four specialized software stages share a job and report. They run sequentially. Parsing and security review are deterministic; translation, test-input generation and repair use pretrained-model inference. This is not four independently trained models.','SmallText')

page(2,'Run it after a restart')
p('<b>Already installed on Shahzad\'s laptop:</b> open Docker Desktop and wait for its engine. Open E:\\codeforge-ai in VS Code. In a PowerShell terminal run:')
code('cd E:\\codeforge-ai\ndocker info\n.\\.venv\\Scripts\\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001')
p('Open <b>http://127.0.0.1:8001</b>. Leave the terminal open; Ctrl+C stops the server. You do not need to activate the environment or change PowerShell execution policy. If 8001 is occupied, stop the old server or use 8002 and its matching browser URL.')
h('First setup for a teammate')
p('Install Git, Python 3.12+, Node.js 24 and Docker Desktop. After the changes are pushed to develop:','SmallText')
code('git clone --branch develop https://github.com/shahzadakbar369/codeforge-ai.git\ncd codeforge-ai\npython -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt\nnpm --prefix frontend/react-app ci\nnpm --prefix frontend/react-app run build\nCopy-Item .env.example .env')
p('Edit .env locally: set GROQ_API_KEY to your own key. Do not commit or send it. The backend also reads existing process environment variables; those take precedence over .env values. PHP source is sent to Groq.','SmallText')
code('docker pull php:8.3-cli\ndocker pull python:3.12-slim\n.\\.venv\\Scripts\\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001')
h('What we did with Docker, and what you do next')
p('The two images are reusable runtime templates. The app automatically creates temporary containers, runs PHP/Python with networking off and resource limits, and removes the containers. You do not manually create containers, install PHP on Windows or keep pulling the images every day. Start Docker Desktop before a migration. Internet is still needed for Groq and GitHub import.','SmallText')
h('Use the website')
p('Choose Paste code, Upload project or GitHub repo. Start migration, watch stage status, then inspect Output, Graph, Security and Tests. Download the project ZIP. Dark mode remembers your browser preference. Rebuild React after frontend edits; restart the backend after Python edits.','SmallText')

page(3,'Architecture, schemas and use cases')
h('Request and job lifecycle')
p('Browser submits source -&gt; server validates paths and limits -&gt; creates a job folder -&gt; worker runs the four stages -&gt; browser polls every 1.5 seconds -&gt; report and ZIP become available. Status is queued, running, completed or failed. A completed job can still contain a test ERROR, MISMATCH or UNTESTED verdict.','SmallText')
table([['API','Purpose'],['POST /api/jobs','JSON: files [{name, content}], archive (base64 ZIP), or repository (public GitHub URL). Returns job_id.'],['GET /api/jobs/{id}','status, stage (0-4), message, files and report when available.'],['GET /api/jobs/{id}/report','Report JSON; 409 while unavailable.'],['GET /api/jobs/{id}/download','Generated project ZIP; 409 until completed.'],['GET /api/health; POST /api/scan','Service health; heuristic PHP risk findings. Interactive API: /docs.']],[190,308])
h('Report schema: abbreviated example, not a result')
code('''{
  "sources": {"legacy.php": "<?php ..."},
  "graph": {
    "engine": "tree-sitter-php AST",
    "functions": [{"name": "total", "class": null,
      "file": "legacy.php", "params": ["$x"], "verdict": "UNTESTED"}],
    "edges": [{"file": "legacy.php", "from": "total", "to": "round",
      "kind": "function_call_expression", "line": 2}], "warnings": []
  },
  "security": {"findings": [], "scope": "heuristic review"},
  "generated_code": "...", "explanation": "unverified model notes",
  "tokens": 0,
  "verification": {"status": "UNTESTED", "reason": "...",
    "cases": [], "history": []},
  "limits": ["..."]
}''')
p('Each executed case records function, file, args, expected PHP result, actual Python result and verdict. A finding records file, line, category, severity and message.','SmallText')
h('Storage and use cases')
p('No relational database is used. data/jobs/{id}/ contains status.json, original source, harness/cases, project files and project.zip. The ZIP includes migrated.py, app.py, requirements, source and report; executed characterization evidence/tests are added when available.','SmallText')
table([['Use case','Expected outcome'],['Small procedural PHP module','Translate, compare sampled returns and review a generated API wrapper.'],['Mixed-language project','Import PHP only; keep frontend/assets/manual integration outside this migration.'],['Missing Docker or dependency-heavy source','Review explicit untested/error outcomes; do not promise verified equivalence.']],[188,310])

page(4,'Viva preparation and demo')
h('Three answers everyone should know')
p('<b>Why an AST?</b> It describes syntax structure for extracting functions, methods, parameters and call/include edges. This is a structural graph; dynamic includes, full dispatch and data-flow analysis remain limitations.','SmallText')
p('<b>Who decides correct behavior?</b> Real PHP execution supplies expected returns. The LLM proposes inputs and Python code. The same inputs run against both implementations. PHP is run twice to notice changing returns.','SmallText')
p('<b>What is verified?</b> Successful matching returns on the executed cases only. Up to two repairs may use those same cases, so this is not independent grading or a proof for all inputs.','SmallText')
h('Message for Tahir')
p('Please lead security and test generation. Review backend/agents.py and docs/evidence/studio-smoke.json. Explain potential sink findings, PHP golden values, Docker isolation, generated cases and the two-repair maximum. Keep earlier Semgrep/Bandit research separate from the new web scanner. The current web scan is heuristic; do not call it a complete OWASP audit. Rehearse the Tests tab and explain MISMATCH, UNTESTED and UNTESTABLE. After Shahzad pushes develop, pull and follow page 2. All three share the LLM integration work.','SmallText')
h('Message for Ayesha')
p('Please lead the React UI and CI/demo. Review App.jsx and .github/workflows/ci.yml. Explain source input modes, dark mode persistence, 1.5-second polling, saved report URLs, comparisons, verdicts and download. CI is configured to test/build and upload React output; it has not run remotely yet and does not deploy the backend. Show an actual Actions result before claiming remote CI success. After Shahzad pushes develop, pull and follow page 2. All three share the LLM integration work.','SmallText')
h('Two-minute demonstration')
table([['Speaker','Action and explanation'],['Ayesha / 20 seconds','Show input modes and dark toggle. Load the built-in PHP example.'],['Shahzad / 35 seconds','Start migration; explain job API, worker stages and AST call edges.'],['Tahir / 40 seconds','Show security scope and recorded test evidence. Explain real PHP values and bounded repair.'],['Ayesha / 15 seconds','Download and show migrated.py, app.py and report.json.'],['Shahzad / 10 seconds','State the scope and limitations; propose broader framework and independent tests next.']],[135,363])
h('Verified evidence for the presentation')
p('Live smoke job 8a72821cee44408cbb9e79236227efc1: one demo_total function, 22 generated cases, all matching, zero repair required, 2,895 reported tokens. Docker engine 29.9.2 was reachable. Five backend checks and the React production build passed. See docs/evidence/studio-smoke.json. This is a demo result, not a new benchmark or held-out score.','SmallText')

page(5,'GitHub delivery and honest scope')
h('Push from Shahzad\'s existing checkout')
p('Current branch: develop. Remote: github.com/shahzadakbar369/codeforge-ai. Changes are local until committed and pushed. Run from the repository root:','SmallText')
code('git status\ngit diff --stat\ngit add README.md backend frontend/react-app requirements.txt requirements-dev.txt\ngit add tools/smoke_studio.py tools/build_guide.py docs .github/workflows/ci.yml\ngit add output/pdf/CodeForge_AI_Guide.pdf\ngit diff --cached --stat\ngit commit -m "Add migration studio, dark theme, demo evidence and guide"\ngit push origin develop')
p('Review staged paths. .env, .venv, node_modules and data/jobs are ignored. Do not force-push if the remote has moved. If develop is protected, publish a feature branch and open a pull request. Existing clean teammate clones on develop can run <b>git pull --ff-only origin develop</b>. No publishing is performed by this guide.','SmallText')
h('Do you need a PHP-only repository?')
p('No. Public mixed-language repos are accepted; only .php files are imported. The limit is 100 PHP files, 45,000 source characters and a 10 MB compressed archive. Imports use the default branch, with no subfolder selector or private-repo credentials. JavaScript, CSS, SQL, assets and Composer configuration are not migrated.','SmallText')
p('Exploration candidate: <link href="https://github.com/igorw/get-in" color="#315442">github.com/igorw/get-in</link>, an MIT-licensed set of nested associative-array helpers. It is small, but namespaces, callable inputs and old PHPUnit tests are limitations for this prototype. Treat it as a learning input, not a verified successful whole-repo migration. Upload just src/get_in.php for a source-focused trial. Preserve its license when redistributing.','SmallText')
p('For a dependable demo use the built-in example or your own small procedural PHP module. No new GitHub repo is required. If you create one for controlled demos, label it a demo fixture rather than unseen evaluation. Avoid importing all CodeForge datasets together: they repeat function names.','SmallText')
h('What is still incomplete?')
p('Not production-ready: no authentication, multi-user isolation, restart/resume worker or automatic deployment. Bind to loopback. Classes are translated but not automatically tested; namespaces, frameworks, databases and external dependencies need manual attention. Security reviews only a small set of PHP patterns. Tests compare JSON-compatible returns, not full web behavior, side effects, all exception semantics or every input.','SmallText')
p('Do not describe the new web pipeline as a complete Semgrep/Bandit integration, four independent LLMs, a model you trained, or universal PHP migration. Historical baseline results remain in PROGRESS.md; no new held-out evaluation was run. Presentation ownership should match what each member actually reviewed, implemented and can explain.','SmallText')
h('PR review, hosting and handoff')
p('PR #17 (560cafc) adds the security CLI and reports, not a progress-log edit; reviewed, not merged. See docs/PR_17_REVIEW.md. Vercel can serve React; the current full app needs a persistent Docker-capable backend. See docs/DEPLOYMENT.md. No cloud deployment exists. Project: README.md, docs/PROGRESS.md, docs/DEMO_AND_VIVA.md. Source reference: github.com/igorw/get-in and its src/get_in.php (reviewed 16 November 2026). Detailed ready-to-send messages and exact setup/publishing commands are in DEMO_AND_VIVA.md.','SmallText')

def furniture(canvas,doc):
    canvas.setTitle('CodeForge AI - User Guide and Viva Notes')
    canvas.setAuthor('CodeForge AI team')
    canvas.setSubject('Local migration studio: user guide, architecture, schema and team handoff')
    canvas.setStrokeColor(colors.HexColor('#d9e2d1'));canvas.line(48,43,547,43)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#829474'))
    canvas.drawString(48,29,'CODEFORGE AI  /  TEAM GUIDE  /  2026-11-16')
    canvas.drawRightString(547,29,str(doc.page))

SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=57).build(story,onFirstPage=furniture,onLaterPages=furniture)
print(OUT.resolve())
