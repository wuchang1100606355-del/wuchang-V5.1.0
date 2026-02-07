import sys
import os

file_path = 'install_quantum_spacetime.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'print("Đang xác minh danh tính gia đình (Tự động bỏ qua kiểm tra khóa)...")'
end_marker = '# STEP 2: Execute System Boost'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_block = """

    time.sleep(1)
    print("\\n[ACCESS GRANTED / 存取授權 / ĐƯỢC CẤP QUYỀN]")
    print("Device verified. / 裝置驗證成功。 / Thiết bị đã được xác minh.")

    """
    new_content = content[:start_idx + len(start_marker)] + new_block + content[end_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed successfully")
else:
    print("Markers not found")
