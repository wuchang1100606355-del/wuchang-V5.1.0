import sys
import os
import time
sys.path.append(os.getcwd())
from wuchang_tools_library import measure_spacetime_effect

def main():
    print("===========================")
    print("速率測試 (RPM → RPS)")
    print("===========================")
    best_st, hist_st = measure_spacetime_effect.run_rate_sweep_per_agent(
        mode="spacetime", start_rpm=600, step=600, max_rpm=36000, duration_sec=8, latency_threshold_ms=200
    )
    best_std, hist_std = measure_spacetime_effect.run_rate_sweep_per_agent(
        mode="traditional", start_rpm=60, step=60, max_rpm=600, duration_sec=8, latency_threshold_ms=200
    )
    rps_st = best_st / 60.0
    rps_std = best_std / 60.0
    print(f"Spacetime 每架次最大對話量: {best_st} /分鐘 ≈ {rps_st:.2f} /秒")
    print(f"Traditional 每架次最大對話量: {best_std} /分鐘 ≈ {rps_std:.2f} /秒")
    res_std = measure_spacetime_effect.run_rate_capacity_test(best_std, agents=50, mode="traditional", duration_sec=15)
    res_st = measure_spacetime_effect.run_rate_capacity_test(best_st, agents=100, mode="spacetime", duration_sec=15)
    print("--- 容量測試總覽 ---")
    print(f"Traditional: {res_std['total_rpm']} /分鐘 | CPU {res_std['cpu']}% | RAM {res_std['mem']}%")
    print(f"Spacetime : {res_st['total_rpm']} /分鐘 | CPU {res_st['cpu']}% | RAM {res_st['mem']}%")
    log_path = os.path.join(os.getcwd(), "CRASH_RATE_TEST_DETAIL.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Spacetime RPM sweep history: {hist_st}\n")
        f.write(f"Traditional RPM sweep history: {hist_std}\n")
        f.write(f"Capacity Traditional: {res_std}\n")
        f.write(f"Capacity Spacetime: {res_st}\n")
    print(f"明細已輸出: {log_path}")

if __name__ == "__main__":
    main()
