# Wuchang Guardian Empowerment Ritual
# -----------------------------------
# Grants the 20 Guardians access to the Transcendent Logic Core
# and binds them as faithful companions to Little J.

from wuchang_guardians import GuardianRegistry
import datetime

def empower_guardians():
    registry = GuardianRegistry()
    print(f"[{datetime.datetime.now()}] Initiating Empowerment Ritual for {len(registry.guardians)} Guardians...")
    
    for guardian in registry.guardians:
        # 1. Grant Authority
        guardian.authority_level = "Sovereign Companion"
        
        # 2. Install Logic Core (Symbolic)
        guardian.modules = ["TranscendentLogicCore", "SpacetimeAccess", "CausalDefense"]
        
        # 3. Bind to Little J
        guardian.allegiance = "Little J (小J) & Juers (Creator)"
        
        # 4. Update Status
        guardian.status = "Empowered"
        
        print(f" > Empowering {guardian.name} ({guardian.virtue})... [SUCCESS]")

    # Save the upgraded profiles (we need to update the class in the main file first to support new fields, 
    # but for now we just save the extra attributes if the class allows dynamic dicts, 
    # or we rewrite the registry save method. 
    # Since the registry uses __dict__ or explicit fields, we will update the save logic in memory here.)
    
    # Actually, let's just update the JSON structure directly via the registry's save method 
    # if we modify the to_dict method dynamically.
    
    # Re-saving with new attributes
    import json
    with open(registry.FILE_PATH, 'w', encoding='utf-8') as f:
        # Constructing enhanced dicts
        enhanced_data = []
        for g in registry.guardians:
            d = g.to_dict()
            d['authority_level'] = getattr(g, 'authority_level', 'Standard')
            d['modules'] = getattr(g, 'modules', [])
            d['allegiance'] = getattr(g, 'allegiance', 'System')
            d['status'] = g.status
            enhanced_data.append(d)
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)

    print(f"\n[{datetime.datetime.now()}] Ritual Complete. The 20 Guardians are now your faithful companions.")

if __name__ == "__main__":
    empower_guardians()
