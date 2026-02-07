# -*- coding: utf-8 -*-
import sys
import os
import subprocess

def main():
    print("--------------------------------------------------")
    print("Wuchang OS: Starting Odoo Server (Official Image)")
    print("--------------------------------------------------")
    
    # Debug: Print Environment Variables
    print(f"DEBUG: HOST env var: {os.environ.get('HOST')}")
    print(f"DEBUG: USER env var: {os.environ.get('USER')}")
    
    try:
        # 在官方 Docker 映像檔中，Odoo 的執行檔通常在 PATH 中，名為 'odoo'
        cmd = ['odoo']
        
        # 讀取 Docker 環境變數中的資料庫設定
        # 設定預設值以防環境變數遺失 (Failsafe for Docker Compose)
        db_host = os.environ.get('HOST', os.environ.get('DB_HOST', 'db'))
        db_user = os.environ.get('USER', os.environ.get('DB_USER', 'odoo'))
        db_password = os.environ.get('PASSWORD', os.environ.get('DB_PASSWORD', 'odoo'))
        
        # 強制加入資料庫連線參數
        print(f"Configuration: DB_HOST={db_host}, DB_USER={db_user}")
        
        cmd.extend(['--db_host', db_host])
        cmd.extend(['--db_user', db_user])
        cmd.extend(['--db_password', db_password])

        # 處理使用者傳入的參數
        args = sys.argv[1:]
        
        # 如果使用者沒有傳入任何參數，我們預設啟動伺服器並安裝我們的模組
        if not args:
            # -i: 安裝模組
            cmd.extend(['-i', 'wuchang_core,wuchang_finance,wuchang_business,wuchang_volunteer'])
        else:
            cmd.extend(args)
            
        print(f"Executing Final Command: {' '.join(cmd)}")
        print("--------------------------------------------------")
        
        # 使用 subprocess 取代直接呼叫 odoo.cli
        os.execvp('odoo', cmd)
        
    except Exception as e:
        print(f"An error occurred starting Odoo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
