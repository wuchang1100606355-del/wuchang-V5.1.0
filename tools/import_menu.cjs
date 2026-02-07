const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');

async function main() {
  const file = process.argv[2];
  if (!file) { console.error('請提供Excel路徑'); process.exit(1); }
  const wb = XLSX.readFile(file);
  const sheet = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(sheet, {defval: ''});
  const excludeCats = new Set(['聊國簡餐類', '手沖咖啡類', '咖啡豆']);
  const items = []; const addons = []; const links = {}; const seenAddon = new Set();
  function num(v){ const n = Number(String(v).replace(/[^0-9.\-]/g,'')); return isNaN(n)?0:n; }

  for (const r of rows) {
    const code = (r['編號']||r['代碼']||'').toString().trim();
    const name = (r['品名']||r['名稱']||'').toString().trim();
    const cat = (r['分類']||'').toString().trim();
    const desc = (r['描述']||r['備註']||'').toString().trim();
    const mPrice = num(r['中杯M']||r['M']||r['中杯']||r['價格']||0);
    const type = (r['類型']||'').toString().trim();
    const isAddon = /加購|加料|選配/i.test(type) || /加購|加料/i.test(name);

    if (isAddon || (!cat || excludeCats.has(cat))) {
      if (!seenAddon.has(code) && name) {
        addons.push({ code, name, delta_price: num(r['加購價']||r['加價']||r['差額']||r['價格']||0), type: type||'addon' });
        seenAddon.add(code);
      }
      continue;
    }
    if (name) {
      items.push({ code, name, base_price: mPrice, category: cat, description: desc });
      links[code] = [];
    }
  }

  for (const r of rows) {
    const code = (r['編號']||r['代碼']||'').toString().trim();
    const name = (r['品名']||r['名稱']||'').toString().trim();
    const type = (r['類型']||'').toString().trim();
    const isAddon = /加購|加料|選配/i.test(type) || /加購|加料/i.test(name);
    if (!isAddon) continue;
    const target = (r['適用編號']||r['主商品編號']||'').toString().trim();
    const delta = num(r['加購價']||r['加價']||r['差額']||r['價格']||0);
    if (target && links[target]) {
      links[target].push({ code, delta_price: delta });
    } else {
      for (const it of items) links[it.code].push({ code, delta_price: delta });
    }
  }

  const attributes = [
    { name:'杯型', key:'cup_size', values: [ {name:'中杯M', delta_price:0}, {name:'大杯L', delta_price:num(rows[0]?.['大杯L']||0)} ], apply_items: items.map(i=>i.code) },
    { name:'糖度', key:'sugar', values: [ {name:'無糖', delta_price:0}, {name:'半糖', delta_price:0}, {name:'全糖', delta_price:0} ], apply_items: items.map(i=>i.code) },
    { name:'溫度', key:'temp', values: [ {name:'熱', delta_price:0}, {name:'冰', delta_price:0} ], apply_items: items.map(i=>i.code) },
  ];

  const payload = { items, addons, links, attributes };
  const url = 'http://localhost:8069/api/menu/import';
  try {
    const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const out = await res.json();
    fs.writeFileSync(path.join(process.cwd(), 'menu_import_result.json'), JSON.stringify({response: out, preview: payload}, null, 2));
    console.log('匯入完成', out);
  } catch (e) {
    fs.writeFileSync(path.join(process.cwd(), 'menu_import_error.txt'), String(e));
    console.error('匯入失敗', e);
    process.exit(2);
  }
}

main();

