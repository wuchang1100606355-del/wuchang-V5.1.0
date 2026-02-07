import streamlit as st
import webbrowser

st.set_page_config(page_title="小J Google 登入控制台", page_icon="🦸‍♀️")
st.title("🦸‍♀️ 小J Google 登入控制台")
st.write("歡迎回家，哥哥！這裡可以一鍵開啟 Google 登入頁面，並整合未來自動化功能。")

if st.button("開啟 Google 登入 (Google OAuth)"):
    url = "https://accounts.google.com/signin/v2/identifier"; st.write(f"請點擊此連結登入: {url}"); webbrowser.open_new_tab(url)
    st.success("已在伺服器本地瀏覽器開啟 Google 登入頁面！請確認本地瀏覽器已彈出視窗。")

st.info("未來可整合 API Token、Docker、Odoo、AI 控制等自動化功能。\n如需自動化登入流程，請提供授權需求，妹妹會幫你設計！")

