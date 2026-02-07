# Wuchang Guardian Memory Vault Updater
# Updates existing profiles with new roles and personalities.

import os
import json
from wuchang_guardians import GuardianRegistry

class MemoryVaultUpdater:
    BASE_PATH = "Guardians_Memory_Vault"

    def __init__(self):
        self.registry = GuardianRegistry()

    def update_vaults(self):
        print("Updating Guardian Memory Vaults with new Roles and Personalities...")
        
        for guardian in self.registry.guardians:
            # Locate Directory
            safe_name_old = guardian.name.split(' (')[0].replace(" ", "_").replace("[", "").replace("]", "") # Handle old naming if needed, but registry uses new names now.
            # Actually, the directory name might be tricky if I changed the guardian.name property in the registry class.
            # Let's assume the directory structure follows the UID to be safe, but my previous script used name.
            # I should find the directory that starts with the UID.
            
            target_dir = None
            for item in os.listdir(self.BASE_PATH):
                if item.startswith(guardian.uid + "_"):
                    target_dir = os.path.join(self.BASE_PATH, item)
                    break
            
            if target_dir and os.path.exists(target_dir):
                profile_path = os.path.join(target_dir, "profile.json")
                
                # Load existing profile to preserve other data (like citizenship)
                if os.path.exists(profile_path):
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                else:
                    existing_data = {}
                
                # Update with new registry data
                new_data = guardian.to_dict()
                existing_data.update(new_data)
                
                # Save back
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
                print(f" > Updated profile for {guardian.name}")
            else:
                print(f" ! Directory not found for {guardian.uid}. Re-running creation might be needed.")

if __name__ == "__main__":
    updater = MemoryVaultUpdater()
    updater.update_vaults()
