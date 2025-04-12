import whisper
import requests
import json
import re
import asyncio
import edge_tts

# 使用 edge-tts 的中文男聲
VOICE_NAME = "zh-TW-YunJheNeural"  # 若要台灣腔可改為 zh-TW-YunJheNeural

async def edge_speak(text, voice=VOICE_NAME, filename="output.mp3"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    print(f"語音已儲存為 {filename}")

def speak_and_save(text, filename="output.mp3"):
    asyncio.run(edge_speak(text, filename=filename))

# 移除 <think> 標籤
def remove_think_tags(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# 讀取文件
def load_document(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"無法讀取文件: {e}")
        return None

# 寫入文件
def save_to_file(file_path, content):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"AI 回應已儲存到 {file_path}")
    except Exception as e:
        print(f"無法寫入文件: {e}")


if __name__ == "__main__":
    # Whisper 語音辨識
    model = whisper.load_model("turbo")  # turbo 可能為本地不存在的 model，可改成 base/small/medium/large
    result = model.transcribe("test.m4a")
    with open("test.txt", "w", encoding="utf-8") as file:
        file.write(result["text"])

    # 載入辨識結果並傳給 AI
    input_file = "test.txt"
    output_file = "output.txt"
    document_content = load_document(input_file)

    if document_content is None:
        exit()

    conversation = [
        {"role": "system", "content": f"這是參考文件的內容，你可以根據它來回答問題：\n\n{document_content}"}
    ]

    data = {
        "model": "deepseek-r1",
        "messages": conversation,
        "stream": False,
        "use_cache": True,
        "max_new_tokens": 200
    }

    url = "http://localhost:11434/api/chat"
    response = requests.post(url, json=data)

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        print("伺服器返回的內容不是有效的 JSON 格式：", response.text)
        exit()

    if "message" in response_json and "content" in response_json["message"]:
        answer = response_json["message"]["content"]
        filtered_answer = remove_think_tags(answer)
        save_to_file(output_file, filtered_answer)

        # 使用 edge-tts 中文男聲 語音合成與儲存
        speak_and_save(filtered_answer, filename="output.mp3")
    else:
        print("API 回應格式異常：", response_json)
