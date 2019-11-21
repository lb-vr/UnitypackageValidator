import json

j = {}

ret = {
    "reference_whitelist": {}
}

with open("rule.json", mode="r", encoding="utf-8") as f:
    j = json.load(f)

for upkg in j["common_packages"]:
    ret["reference_whitelist"][upkg["name"]] = {}
    for a in upkg["assets"]:
        ret["reference_whitelist"][upkg["name"]][a["guid"]] = {"path": a["path"]}

with open("rule_new.json", mode="w", encoding="utf-8") as f:
    json.dump(ret, f)
