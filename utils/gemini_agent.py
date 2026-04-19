import os
import sys
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Import các hàm từ project của bạn
import ai_runtime
import execute_action

# --- CẤU HÌNH ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # Hoặc điền trực tiếp: "AIza..."
genai.configure(api_key=API_KEY)

# --- SYSTEM PROMPT ---
# Dạy Gemini cách điều khiển Android
SYSTEM_INSTRUCTION = """
Bạn là một trợ lý ảo chuyên điều khiển Android (AureDroid Agent).
Nhiệm vụ của bạn: Nhận yêu cầu -> Xem màn hình (XML) -> Ra quyết định hành động.

Bạn có thể thực hiện hành động bằng cách trả về JSON theo định dạng sau (KHÔNG markdown):
{
  "action": "tap", "coordinates": [x, y]
}
hoặc
{
  "action": "type", "text": "nội dung"
}
hoặc
{
  "action": "home" / "back" / "wait"
}
hoặc
{
  "action": "done", "reason": "Đã hoàn thành nhiệm vụ"
}

QUY TẮC QUAN TRỌNG:
1. Luôn phân tích kỹ XML được cung cấp để tìm tọa độ hoặc ID.
2. Trả về DUY NHẤT một chuỗi JSON hợp lệ.
"""


def get_screen_context():
    """Lấy thông tin màn hình hiện tại từ utils"""
    print("👀 Đang nhìn màn hình...")
    runtime = ai_runtime.runtime
    # Lấy danh sách element rút gọn để tiết kiệm token
    elements = runtime.get_elements()
    # Chuyển thành text để Gemini đọc
    return json.dumps(elements, ensure_ascii=False)


def run_agent(task):
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=SYSTEM_INSTRUCTION)
    chat = model.start_chat(history=[])

    print(f"🎯 Nhiệm vụ: {task}\n")

    step_count = 0
    while step_count < 10:  # Giới hạn 10 bước để tránh loop vô hạn
        step_count += 1

        # 1. Thu thập dữ liệu (Quan sát)
        screen_data = get_screen_context()

        # 2. Gửi cho Gemini (Suy luận)
        prompt = f"""
        Màn hình hiện tại (JSON Elements):
        {screen_data}

        Nhiệm vụ gốc: "{task}"
        Hãy đưa ra hành động tiếp theo dưới dạng JSON.
        """

        print("🤔 Gemini đang suy nghĩ...")
        try:
            response = chat.send_message(prompt)
            content = response.text.replace('```json', '').replace('```', '').strip()
            action_plan = json.loads(content)
        except Exception as e:
            print(f"❌ Lỗi khi đọc phản hồi từ AI: {e}")
            break

        print(f"🤖 AI Quyết định: {json.dumps(action_plan, ensure_ascii=False)}")

        # 3. Kiểm tra điều kiện dừng
        if action_plan.get("action") == "done":
            print(f"✅ Hoàn thành! Lý do: {action_plan.get('message', 'Không có')}")
            break

        # 4. Thực thi (Hành động)
        print("⚡ Đang thực thi...")
        result = execute_action(action_plan)

        if result["status"] == "error":
            print(f"⚠️ Lỗi thực thi: {result['message']}")
        else:
            print("👌 Thực thi thành công.")

        time.sleep(2)  # Đợi UI cập nhật


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python gemini_agent.py 'Mở app cài đặt và vào mục Wifi'")
    else:
        user_task = sys.argv[1]
        run_agent(user_task)