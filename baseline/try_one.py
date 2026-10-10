import os, json, ast
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

php = open("baseline/scratch/invoice.php", encoding="utf-8").read()

prompt = (
    "You migrate legacy PHP to modern Python 3. "
    "Return ONLY a JSON object with keys: generated_code (string), explanation (string). "
    "Keep behavior identical, including rounding. No markdown fences.\n\nPHP:\n" + php
)

r = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    max_completion_tokens=3000,
)
text = r.choices[0].message.content
print("tokens used:", r.usage.total_tokens)

try:
    data = json.loads(text)
except json.JSONDecodeError:
    print("Model did not return valid JSON:")
    print(text)
    raise SystemExit(1)

code = data["generated_code"]
try:
    ast.parse(code)
    print("syntax: OK")
except SyntaxError as e:
    print("syntax error:", e)

open("baseline/scratch/invoice_migrated.py", "w", encoding="utf-8").write(code)
print(data["explanation"])