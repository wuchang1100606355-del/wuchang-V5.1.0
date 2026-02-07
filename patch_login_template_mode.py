import re
p = r"c:/wuchang V5.1.0/wuchang_os/addons/wuchang_design_system/views/web_login_templates.xml"
with open(p,'r',encoding='utf-8') as f:
    s = f.read()
changed = False
# After branding_info fetch, inject mode-based hiding
s = s.replace(
"if (pn && d.patent_no) { pn.textContent = '專利字號：' + d.patent_no; }\n                    } catch(e) { console.error('Branding load failed', e); }",
"if (pn && d.patent_no) { pn.textContent = '專利字號：' + d.patent_no; }\n                        var mode = d && d.home_mode || '';\n                        if (mode === 'personal') {\n                            var hero = document.querySelector('.whc-hero'); if (hero) hero.style.display = 'none';\n                            var heroCap = document.querySelector('.whc-hero-caption'); if (heroCap) heroCap.style.display = 'none';\n                            var assocAlert = document.querySelector('.alert.alert-dark.text-center'); if (assocAlert) assocAlert.style.display = 'none';\n                            var brandBox = document.getElementById('branding_info'); if (brandBox) brandBox.style.display = 'none';\n                            var vb = document.getElementById('login_video_box'); if (vb) vb.style.display = 'none';\n                            var ab = document.getElementById('login_audio_box'); if (ab) ab.style.display = 'none';\n                            var mq = document.getElementById('marquee_wrap'); if (mq) mq.style.display = 'none';\n                        }\n                    } catch(e) { console.error('Branding load failed', e); }"
)
with open(p,'w',encoding='utf-8') as f:
    f.write(s)
print('patch_login_template home_mode toggle applied')
