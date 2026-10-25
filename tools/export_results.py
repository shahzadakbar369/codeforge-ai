"""Turns the baseline results into frontend/data/results.js (real numbers only)."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results" / "baseline"
DEV = ROOT / "datasets" / "dev"
OUT = ROOT / "frontend" / "data" / "results.js"


def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def legacy_source(folder):
    files = [folder / "legacy.php"] + sorted(p for p in folder.glob("*.php") if p.name != "legacy.php")
    return "\n\n".join(
        f"// ===== FILE: {p.name} =====\n{p.read_text(encoding='utf-8')}" for p in files if p.exists()
    )


def main():
    generation = {r["program"]: r for r in load(RES / "generation.json", [])}
    comparison = {r["program"]: r for r in load(RES / "comparison.json", [])}
    programs = []
    for name in sorted(set(generation) | set(comparison)):
        gen, cmp_ = generation.get(name, {}), comparison.get(name, {})
        notes = load(RES / name / "migration.json", {})
        code_file = RES / name / "migrated.py"
        programs.append({
            "name": name,
            "counted": cmp_.get("counted", not name.startswith("00_")),
            "model": gen.get("model"),
            "tokens": gen.get("tokens"),
            "generation_status": gen.get("status"),
            "comparison_status": cmp_.get("status"),
            "legacy_php": legacy_source(DEV / name) if (DEV / name).exists() else "",
            "migrated_python": code_file.read_text(encoding="utf-8") if code_file.exists() else "",
            "explanation": notes.get("explanation", ""),
            "assumptions": notes.get("assumptions", []),
            "warnings": notes.get("warnings", []),
            "functions": [
                {k: f.get(k) for k in ("function", "verdict", "total", "matched", "failures")}
                for f in cmp_.get("functions", [])
            ],
        })
    counted = [f for p in programs if p["counted"] for f in p["functions"]]
    equivalent = sum(1 for f in counted if f["verdict"] == "EQUIVALENT")
    data = {
        "generated_on": date.today().isoformat(),
        "summary": {
            "programs": sum(1 for p in programs if p["counted"]),
            "functions_compared": len(counted),
            "equivalent": equivalent,
        },
        "programs": programs,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.CODEFORGE_RESULTS = " + json.dumps(data, indent=2) + ";\n", encoding="utf-8")
    print(f"wrote {OUT}: {equivalent} of {len(counted)} functions equivalent")


if __name__ == "__main__":
    main()