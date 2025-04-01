import whisper
import pyttsx3

model = whisper.load_model("turbo")
result = model.transcribe("test.m4a")
with open("test.txt", "w", encoding="utf-8") as file:
    file.write(result["text"])


import requests, json
import re  # 用於過濾 <think> 內容

def load_document(file_path):
    """讀取文件內容，並返回字串"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"無法讀取文件: {e}")
        return None

def save_to_file(file_path, content):
    """將內容寫入文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"AI 回應已儲存到 {file_path}")
    except Exception as e:
        print(f"無法寫入文件: {e}")

def remove_think_tags(text):
    """移除 <think> 標籤及其內容"""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


 
def speak(txt):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)
    engine.say(txt)
    engine.runAndWait()
    

if __name__ == "__main__":
    input_file = "test.txt"   # 讀取的文檔
    output_file = "output.txt"  # 儲存 AI 回應的文檔
    document_content = load_document(input_file)

    if document_content is None:
        exit()

    conversation = [
        {"role": "system", "content": f"這是參考文件的內容，你可以根據它來回答問題：\n\n{document_content}"}
    ]

    data = {
        "model": "deepseek-r1",
        "messages": conversation,
        "stream": False
    }

    url = "http://localhost:11434/api/chat"
    response = requests.post(url, json=data)

    try:
        response_json = response.json()  # 解析 JSON
    except json.JSONDecodeError:
        print("伺服器返回的內容不是有效的 JSON 格式：", response.text)
        exit()

    if "message" in response_json and "content" in response_json["message"]:
        answer = response_json["message"]["content"]
        filtered_answer = remove_think_tags(answer)  # 移除 <think> 標籤內容
        save_to_file(output_file, filtered_answer)  # 存入 output.txt
        speak(filtered_answer)
    else:
        print("API 回應格式異常：", response_json)

    exit()  # 直接結束程式
