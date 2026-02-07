import uvicorn

if __name__ == "__main__":
    print("✨ 啟動 Wuchang AI VM 端口服務器...")
    print("🚀 服務器正在運行於 http://0.0.0.0:8080")
    uvicorn.run("vm_fastapi_main_new:app",
                host="0.0.0.0", port=8080, reload=False)
