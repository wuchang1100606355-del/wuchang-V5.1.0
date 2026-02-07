from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    property_management_role = fields.Selection([
        ('association', '社區發展協會'),
        ('committee', '公寓大廈管委會'),
        ('government', '里辦公處/政府機關'),
        ('vendor', '合作廠商'),
        ('resident', '一般住戶')
    ], string='物業管理角色', default='resident')

    spatial_idx_lat = fields.Float('緯度', digits=(10, 7))
    spatial_idx_lng = fields.Float('經度', digits=(10, 7))
    spatial_idx_alt = fields.Float('高度', digits=(10, 2))
    spatial_ref_uuid = fields.Char('時空參考 UUID')


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:05:33
---
