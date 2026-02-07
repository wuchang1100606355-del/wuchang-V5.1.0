import os
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize

# 1. 檢查原始碼是否存在
source_file = "staps_kernel_service.py"
if not os.path.exists(source_file):
    print(f"[ERROR] 找不到核心檔案: {source_file}")
    sys.exit(1)

print(f"[BLACKBOX] 正在啟動 STAPS 核心封裝程序...")
print(f"[TARGET] 目標：將 {source_file} 編譯為機器碼...")

# 2. 定義編譯設定
extensions = [
    Extension(
        name="staps_core", # 編譯後的模組名稱 (import staps_core)
        sources=[source_file], # 來源檔案
        extra_compile_args=["-O3"], # 開啟最高級別優化
    )
]

# 3. 執行編譯
try:
    setup(
        name="Wuchang STAPS Kernel",
        ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
        script_args=["build_ext", "--inplace"]
    )
    print("\n" + "="*50)
    print("[SUCCESS] 黑盒封裝完成！")
    print("[INFO] 您現在可以刪除 .py 原始碼，只保留 .pyd/.so 檔案給客戶。")
    print("[INFO] 客戶端調用方式: import staps_core")
    print("="*50)
except Exception as e:
    print(f"[FAIL] 編譯失敗: {e}")
    print("請確保已安裝 C++ 編譯器 (如 Visual Studio Build Tools 或 GCC)")
