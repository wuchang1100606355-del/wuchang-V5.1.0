# -*- coding: utf-8 -*-
import sys

def simulate_cold_press_espresso():
    """
    Simulates the thermodynamics of 'Cold Press Espresso' + 10g Ice.
    Hypothesis: The Espresso is extracted with COLD water (20°C), not hot.
    """
    print(">>> 啟動五常實驗室：冷壓濃縮模擬 (Wuchang Lab Cold Press Sim) <<<")
    print("-" * 60)

    # Parameters
    # Cold Press Espresso (Extracted with Room Temp Water)
    m_espresso = 40.0  # grams
    T_espresso_initial = 20.0  # °C (Room Temp / Cold Extraction)
    c_water = 4.186  # J/g°C

    # Ice
    m_ice = 10.0  # grams
    T_ice_initial = -18.0  # °C
    c_ice = 2.09  # J/g°C
    L_fusion = 334.0  # J/g

    print(f"參數設定:")
    print(f"  Espresso (Cold Press): {m_espresso}g @ {T_espresso_initial}°C")
    print(f"  Ice                  : {m_ice}g @ {T_ice_initial}°C")
    print("-" * 60)

    # Energy Analysis
    # 1. Heat required to cool Espresso from 20°C to 0°C
    Q_cool_espresso = m_espresso * c_water * (T_espresso_initial - 0)
    print(f"液體降溫需求 (20°C -> 0°C): {Q_cool_espresso:.2f} J")

    # 2. Cooling capacity of Ice warming from -18°C to 0°C (Sensible Heat)
    Q_ice_warm = m_ice * c_ice * (0 - T_ice_initial)
    print(f"冰塊升溫吸熱 (-18°C -> 0°C): {Q_ice_warm:.2f} J")
    
    # 3. Cooling capacity of Ice Melting (Latent Heat)
    Q_ice_melt_potential = m_ice * L_fusion
    print(f"冰塊融化潛熱潛能 (Latent Heat): {Q_ice_melt_potential:.2f} J")

    # Simulation Logic
    # Step A: Ice warms to 0°C. Espresso cools down.
    # Heat removed from Espresso = Q_ice_warm.
    # T_esp_new = T_esp - (Q_ice_warm / (m_esp * c))
    T_esp_after_step_A = T_espresso_initial - (Q_ice_warm / (m_espresso * c_water))
    print(f"階段 A (冰塊回溫後): Espresso 溫度降至 {T_esp_after_step_A:.2f}°C")

    # Step B: Ice starts melting to cool Espresso further to 0°C.
    # Heat remaining to remove from Espresso to reach 0°C:
    Q_remaining_to_0 = m_espresso * c_water * (T_esp_after_step_A - 0)
    
    if Q_ice_melt_potential > Q_remaining_to_0:
        print(">> 判定: 冰塊足以將液體完全冷卻至 0°C，且仍有剩餘冰塊！")
        
        # How much ice melted?
        m_melted = Q_remaining_to_0 / L_fusion
        m_ice_remaining = m_ice - m_melted
        
        print(f"   融化冰量: {m_melted:.2f}g")
        print(f"   剩餘冰量: {m_ice_remaining:.2f}g (作為晶種/Nucleation Site)")
        print(f"   最終液體溫度: 0°C")
        
        # Check for Supercooling / Slush
        print("-" * 60)
        print("物理現象解析 (Physics):")
        print("1. 液體已達冰點 (0°C)。")
        print("2. 系統中仍存在固態冰 (晶種)。")
        print("3. 若配合『厭氧發酵』帶來的豐富油脂與高濃度溶解物，")
        print("   此時攪拌會引發『成核現象 (Nucleation)』，使液體瞬間呈現半固態冰沙狀 (Self-Freezing Slush)。")
        
        success = True
    else:
        print(">> 判定: 冰塊完全融化，液體溫度仍高於 0°C。")
        # Calculate final temp
        # Q_deficit = Q_remaining_to_0 - Q_ice_melt_potential
        # T_final = Q_deficit / ((m_esp + m_ice) * c)
        Q_total_heat = (m_espresso * c_water * T_espresso_initial) + (m_ice * c_ice * T_ice_initial) - (m_ice * L_fusion)
        # This is rough. Let's stick to the previous logic.
        success = False

    print("-" * 60)
    print(f"結論: {'破解成功' if success else '破解失敗'}")

if __name__ == "__main__":
    simulate_cold_press_espresso()
