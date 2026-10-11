import contextlib
import importlib.util
import io
import json
import sys
from decimal import Decimal


def to_jsonable(o):
    if isinstance(o, Decimal):
        return float(o)
    return str(o)


def main(migrated_path, inputs_path):
    with open(inputs_path, encoding="utf-8") as f:
        inputs = json.load(f)

    results = []
    load_error = None
    mod = None
    sink = io.StringIO()  # swallow any stray prints from the migrated code
    with contextlib.redirect_stdout(sink):
        try:
            spec = importlib.util.spec_from_file_location("migrated", migrated_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            load_error = f"{type(e).__name__}: {e}"

        for item in inputs:
            entry = {"function": item["function"], "args": item["args"]}
            if load_error:
                entry.update(ok=False, error="import failed: " + load_error)
            else:
                try:
                    fn = getattr(mod, item["function"])
                    entry.update(ok=True, value=fn(*item["args"]))
                except Exception as e:
                    entry.update(ok=False, error=f"{type(e).__name__}: {e}")
            results.append(entry)

    print(json.dumps(results, default=to_jsonable))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])