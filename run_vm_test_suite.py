import sys
import os
import time
import webbrowser
sys.path.append(os.getcwd())
from wuchang_tools_library import measure_spacetime_effect
from wuchang_tools_library import generate_comparison_dashboard

def main():
    print("========================================================")
    print("🌌 時空黑科技極限效能測試套件 (Spacetime Limit Test Suite)")
    print("========================================================")
    print("本程式將執行三階段測試，直到系統崩潰或達到極限：")
    print("1. 傳統架構 (Standard): 模擬硬碟 I/O 瓶頸")
    print("2. 時空架構 (Spacetime): 啟動記憶體鏡像技術")
    print("3. 🔥 崩潰測試 (Crash Test): 逐漸加大壓力直到極限")
    print("--------------------------------------------------------")

    # Setup Environment
    measure_spacetime_effect.setup_test_env()

    try:
        # Configure Load
        ops = 100
        measure_spacetime_effect.NUM_OPERATIONS = ops

        # 1. Run Standard
        print("\n[Phase 1] 傳統架構基準測試 (Standard Mode)...")
        std_duration = measure_spacetime_effect.run_standard_benchmark()
        print(f"   -> 耗時: {std_duration:.2f} 秒")

        # 2. Run Spacetime
        print("\n[Phase 2] 時空架構基準測試 (Spacetime Mode)...")
        st_duration = measure_spacetime_effect.run_spacetime_benchmark()
        print(f"   -> 耗時: {st_duration:.2f} 秒")

        # 3. Crash Test
        print("\n[Phase 3] 🔥 啟動極限崩潰測試 (Crash Test Mode)...")
        print("   -> 警告: 將持續增加 AI 代理人數量，直到系統卡頓或崩潰...")
        print("   -> 目標: 找出「死亡交叉點」(Breaking Point)")

        # Start from 2500 as per user request (slightly below previous max of 3000)
        # Push to 6000 to find real limit
        limit, status, history = measure_spacetime_effect.run_crash_test(max_agents=10000, start_agents=6000, step=200)
        print(f"   -> 測試結束! 狀態: {status}")
        print(f"   -> 時空架構極限: {limit} Concurrent Agents")

        # Calculate Results
        std_data = {"duration": std_duration, "operations": ops}
        st_data = {"duration": st_duration, "operations": ops}
        crash_data = {"limit": limit, "status": status, "history": history}

        speedup = std_duration / st_duration if st_duration > 0 else 9999
        print("\n========================================================")
        print(f"🎉 測試完成! 時空架構效能提升: {speedup:.1f} 倍")
        print(f"�� 系統極限承載: {limit} Agents ({status})")
        print("========================================================")

        # 3. Generate Dashboard
        print("\n正在生成視覺化儀表板 (Generating Dashboard)...")
        generate_comparison_dashboard.generate_html_dashboard(std_data, st_data, crash_data)

        output_path = os.path.join(os.getcwd(), "public_html", "SPACETIME_VS_LEGACY_DASHBOARD.html")
        print(f"報告已生成: {output_path}")

        # 4. Open
        print("正在開啟報告...")
        webbrowser.open(f"file://{output_path}")

    finally:
        # Cleanup
        measure_spacetime_effect.cleanup_test_env()

if __name__ == "__main__":
    main()
