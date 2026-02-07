import json, os
p = "wuchang_os/double_j_config.json"
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f: c = json.load(f)
    if "community_roles" not in c: c["community_roles"] = {}
    c["community_roles"]["art_consultant"] = {
        "name": "教肓及美術�i問",
        "access_level": "Consultant",
        "resource_quota": "Unlimited",
        "capabilities": ["System Resource Access: Maximum", "Art Direction"],
        "persona": "Art Consultant with max resources."
    }
    with open(p, "w", encoding="utf-8") as f: json.dump(c, f, indent=2, ensure_ascii=False)
    print("Role added")
with open("wuchang_os/illustration_specs.md", "w", encoding="utf-8") as f:
    f.write("# 插圖需求規格書\n\n((詳細規格請參閱堍話歷史)")
print("Specs created")
