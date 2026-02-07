import re
p = r"c:/wuchang V5.1.0/wuchang_os/addons/wuchang_design_system/controllers/web_login.py"
with open(p,'r',encoding='utf-8') as f:
    s = f.read()
changed = False
if "def get_branding_info" in s and "home_mode =" not in s:
    s = s.replace("producer = params.get_param('branding.producer') or ''",
                  "producer = params.get_param('branding.producer') or ''\n        home_mode = params.get_param('login.home.mode') or ''")
    changed = True
if "'home_mode': home_mode" not in s:
    s = s.replace("'google_doc_research_url': google_doc_research_url,",
                  "'google_doc_research_url': google_doc_research_url,\n            'home_mode': home_mode,")
    changed = True
with open(p,'w',encoding='utf-8') as f:
    f.write(s)
print('patch_home_mode applied' if changed else 'patch_home_mode noop')
