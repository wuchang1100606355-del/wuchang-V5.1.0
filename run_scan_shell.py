import json
import sys

def run():
    print("=== WUCHANG SYSTEM DIAGNOSTIC SCAN ===")
    
    # 1. Check Module Status
    module = env['ir.module.module'].search([('name', '=', 'wuchang_core')])
    print(f"[Module] wuchang_core: {module.state}")
    
    # 2. Check Committee/Association Partners (Jurisdiction Check)
    print("\n[Jurisdiction Check] Scanning Committees & Associations...")
    partners = env['res.partner'].search([
        ('property_management_role', 'in', ['association', 'committee'])
    ])
    
    valid_jurisdiction = ['五常', '五順', '仁忠']
    
    for p in partners:
        is_valid = any(v in (p.comment or '') for v in valid_jurisdiction) or '五常' in p.name
        status = "ACTIVE" if p.active else "INACTIVE"
        validity = "VALID" if is_valid else "INVALID (Non-Jurisdiction)"
        
        print(f" - [{p.id}] {p.name} ({status}) - {validity}")
        print(f"   Address: {p.city}{p.street2}{p.street}")
        print(f"   Role: {p.property_management_role}")
        print(f"   Coords: ({p.spatial_idx_lat}, {p.spatial_idx_lng})")
        
        # Auto-correction suggestion (we won't delete here, just report)
        if not is_valid:
             print("   -> ACTION NEEDED: DELETE")
        elif not p.active:
             print("   -> ACTION NEEDED: ACTIVATE")

    # 3. Spatiotemporal Index Build
    print("\n[Spatiotemporal Index] Building Index...")
    Monitor = env['wuchang.ai.hallucination.monitor']
    monitor = Monitor.search([], limit=1)
    if not monitor:
        monitor = Monitor.create({'name': 'System Scanner'})
        
    monitor.action_build_system_index()
    env.cr.commit()
    
    # 4. Report Index Stats
    monitor.invalidate_recordset()
    index_json = monitor.system_structure_index
    if index_json:
        data = json.loads(index_json)
        spatial_idx = data.get('spatiotemporal_index', {})
        print(f"Index Built Successfully.")
        print(f" - System Models: {len(data.get('system_structure', {}))}")
        print(f" - Spatiotemporal Entities: {len(spatial_idx)}")
    else:
        print("ERROR: Index failed to build.")

run()
