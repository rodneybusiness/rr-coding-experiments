import yaml, sys
from pathlib import Path

def load_yaml(p): 
    with open(p, "r") as f: 
        return yaml.safe_load(f) or []

areas = load_yaml(Path("schema/areas.yaml"))
subs  = load_yaml(Path("schema/sub_areas.yaml"))

# Basic checks
ids = set()
for a in areas:
    assert a["id"] not in ids, f"Duplicate id: {a['id']}"
    ids.add(a["id"])

for s in subs:
    assert s["id"] not in ids, f"Duplicate id: {s['id']}"
    ids.add(s["id"])
    assert any(a["id"] == s["parent"] for a in areas), f"Unknown parent for {s['id']}"

print("Validation OK. Areas:", len(areas), "Sub-areas:", len(subs))
