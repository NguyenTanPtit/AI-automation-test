# test_manual.py
import os
import sys

# Thêm đường dẫn để import được utils
sys.path.append(os.getcwd())

from ai_runtime import runtime

print("🔄 Đang thử kết nối thiết bị...")
# Thử lấy XML màn hình
xml = runtime._get_xml()

if xml:
    print("✅ Đã lấy được XML màn hình!")
    print(f"📄 Độ dài file XML: {len(xml)} ký tự")

    # Thử tìm một nút (ví dụ nút Settings hoặc nút bất kỳ có text)
    # Lưu ý: Cần mở màn hình có text trước khi chạy
    elements = runtime.get_elements()
    print(f"🔎 Tìm thấy {len(elements)} phần tử có thể tương tác.")
    if len(elements) > 0:
        print("Ví dụ phần tử đầu tiên:", elements[0])
else:
    print("❌ Không lấy được XML. Kiểm tra lại kết nối ADB.")
