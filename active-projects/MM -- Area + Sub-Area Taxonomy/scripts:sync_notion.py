import os, yaml, time
from pathlib import Path
from notion_client import Client

NOTION_TOKEN = os.environ["NOTION_TOKEN"]

with open("mapping/notion_mapping.yaml","r") as f:
    MAP = yaml.safe_load(f)

with open("schema/areas.yaml","r") as f:
    AREAS = yaml.safe_load(f) or []
with open("schema/sub_areas.yaml","r") as f:
    SUBS = yaml.safe_load(f) or []

notion = Client(auth=NOTION_TOKEN)

def _options_from_names(names):
    # Notion Select options need name + (optional) color
    return [{"name": n} for n in names]

def update_select_options(database_id, prop_name, names):
    db = notion.databases.retrieve(database_id=database_id)
    props = db["properties"]
    if prop_name not in props:
        raise RuntimeError(f"Property '{prop_name}' not found in DB {database_id}")
    prop = props[prop_name]
    prop_type = prop["type"]
    if prop_type not in ("select", "multi_select"):
        raise RuntimeError(f"Property '{prop_name}' must be select/multi_select")
    body = {
        "properties": {
            prop_name: {
                prop_type: {
                    "options": _options_from_names(names)
                }
            }
        }
    }
    notion.databases.update(database_id=database_id, **body)

def upsert_taxonomy_page(db_id, name, typ, code=None, parent_page_id=None):
    # naive upsert by searching Code (preferred) else Name
    filter_ = {"property": MAP["taxonomy"]["code_property"], "rich_text": {"equals": code}} if code else \
              {"property": MAP["taxonomy"]["name_property"], "title": {"equals": name}}
    q = notion.databases.query(database_id=db_id, filter=filter_)
    props = {
        MAP["taxonomy"]["name_property"]: {"title":[{"text":{"content": name}}]},
        MAP["taxonomy"]["type_property"]: {"select":{"name": typ}}
    }
    if code:
        props[MAP["taxonomy"]["code_property"]] = {"rich_text":[{"text":{"content": code}}]}
    if parent_page_id:
        props[MAP["taxonomy"]["parent_property"]] = {"relation":[{"id": parent_page_id}]}

    if q["results"]:
        notion.pages.update(page_id=q["results"][0]["id"], properties=props)
        return q["results"][0]["id"]
    else:
        page = notion.pages.create(parent={"database_id": db_id}, properties=props)
        return page["id"]

def build_name_list(items): 
    # keep order by sort
    return [i["name"] for i in sorted(items, key=lambda x: x.get("sort", 0)) if i.get("status","active")=="active"]

def main():
    # 1) update select options on Projects + Goals
    area_names = build_name_list(AREAS)
    sub_names  = build_name_list(SUBS)

    if "projects" in MAP:
        update_select_options(MAP["projects"]["database_id"], MAP["projects"]["area_property"],   area_names)
        update_select_options(MAP["projects"]["database_id"], MAP["projects"]["subarea_property"], sub_names)
    if "goals" in MAP:
        update_select_options(MAP["goals"]["database_id"], MAP["goals"]["area_property"], area_names)

    # 2) (optional) upsert into dedicated Taxonomy DB, preserving parent relations
    if "taxonomy" in MAP and MAP["taxonomy"].get("database_id"):
        dbid = MAP["taxonomy"]["database_id"]
        # upsert areas first
        area_page_ids = {}
        for a in AREAS:
            pid = upsert_taxonomy_page(dbid, a["name"], "Area", a.get("code"))
            area_page_ids[a["id"]] = pid
            time.sleep(0.2)  # gentle rate limiting

        # then sub-areas (link to parent)
        for s in SUBS:
            parent_pid = area_page_ids.get(s["parent"])
            upsert_taxonomy_page(dbid, s["name"], "Sub-Area", s.get("code"), parent_pid)
            time.sleep(0.2)

if __name__ == "__main__":
    main()
