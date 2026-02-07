import re

p = r'c:/wuchang V5.1.0/wuchang_os/addons/wuchang_design_system/views/web_login_templates.xml'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

pattern = r"var mode = d && d.home_mode \|\| '';\s+if \(mode === 'personal'\) \{[^}]+\}"

replacement = r"""var mode = d && d.home_mode || '';
                        if (mode === 'personal' || mode === 'coffee') {
                            var assocAlert = document.querySelector('.alert.alert-dark.text-center'); if (assocAlert) assocAlert.style.display = 'none';
                            var brandAssoc = document.getElementById('brand_association'); if (brandAssoc) brandAssoc.style.display = 'none';
                        }
                        if (mode === 'personal') {
                            var hero = document.querySelector('.whc-hero'); if (hero) hero.style.display = 'none';
                            var heroCap = document.querySelector('.whc-hero-caption'); if (heroCap) heroCap.style.display = 'none';
                            var brandBox = document.getElementById('branding_info'); if (brandBox) brandBox.style.display = 'none';
                            var vb = document.getElementById('login_video_box'); if (vb) vb.style.display = 'none';
                            var ab = document.getElementById('login_audio_box'); if (ab) ab.style.display = 'none';
                            var mq = document.getElementById('marquee_wrap'); if (mq) mq.style.display = 'none';
                        }"""

s_new = re.sub(pattern, replacement, s, flags=re.DOTALL)

if s != s_new:
    print("Patching web_login_templates.xml...")
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s_new)
    print("Done.")
else:
    print("Pattern not found or already patched.")
