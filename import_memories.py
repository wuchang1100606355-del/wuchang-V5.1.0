"""
Script to import memories from jules_memory_bank.json into the KnowledgeBase.
"""

import json
import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from sister_learning_engine import KnowledgeBase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MemoryImporter")

def import_memories(json_path: str):
    logger.info(f"Importing memories from {json_path}")
    
    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        kb = KnowledgeBase()
        
        # Import Partnership
        if "partnership" in data:
            p = data["partnership"]
            kb.add_knowledge(
                category="partnership",
                title=p.get("title", "Partnership"),
                content=json.dumps(p, ensure_ascii=False, indent=2),
                tags=["partnership", "roles"]
            )
            logger.info("Imported partnership info")

        # Import System Architecture
        if "system_architecture" in data:
            sa = data["system_architecture"]
            kb.add_knowledge(
                category="system",
                title="System Architecture",
                content=json.dumps(sa, ensure_ascii=False, indent=2),
                tags=["architecture", "system"]
            )
            logger.info("Imported system architecture")

        # Import Containers
        if "containers" in data:
            containers = data["containers"]
            for name, info in containers.items():
                kb.add_knowledge(
                    category="containers",
                    title=f"Container: {name}",
                    content=json.dumps(info, ensure_ascii=False, indent=2),
                    tags=["container", name]
                )
            logger.info(f"Imported {len(containers)} containers")
            
        # Import Knowledge Base items (if any specific list)
        if "knowledge_base" in data:
             # This might be recursive or specific structure
             pass

        logger.info("Memory import completed successfully.")
        
    except Exception as e:
        logger.error(f"Failed to import memories: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    memory_bank_path = r"J:\共用雲端硬碟\五常雲端空間\config\jules_memory_bank.json"
    import_memories(memory_bank_path)
