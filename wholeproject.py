import whisper
import requests
import json
import re
import asyncio
import edge_tts
import os

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
    yee=0
    with open("content_log.txt", "w", encoding="utf-8") as file:
        file.write("")
    # Whisper 語音辨識
    model = whisper.load_model("turbo")  # turbo 可能為本地不存在的 model，可改成 base/small/medium/large
    
    while 1 :
        input_audio = input("Enter input aduio file : ")
        if not os.path.exists(input_audio):
            print("找不到檔案，請確認路徑正確！")
            continue
        result = model.transcribe(input_audio)
        with open("test.txt", "w", encoding="utf-8") as file:
            file.write(result["text"])

        print("----Whisper Done----")

        # 載入辨識結果並傳給 AI
        input_file = "test.txt"
        output_file = "output.txt"
        log_file = "content_log.txt"
        prompt_file = "prompt.txt"

        document_content = load_document(input_file)
        document_content_log = load_document(log_file)
        prompt_template = load_document(prompt_file)

        if None in (document_content, document_content_log, prompt_template):
            exit()
        
        prompt = prompt_template.replace("{document_content}", document_content)\
                            .replace("{document_content_log}", document_content_log)

        print("----實際 Prompt----")
        print(prompt)

        conversation = [
            {"role": "system", "content": prompt}
        ]

        data = {
            "model": "deepseek-r1",
            "messages": conversation,
            "stream": False,
            "use_cache": True,
            "max_new_tokens": 40
        }


        url = "http://localhost:11434/api/chat"
        response = requests.post(url, json=data)

        print("----DeepSeek Done----")

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("伺服器返回的內容不是有效的 JSON 格式：", response.text)
            exit()

        if "message" in response_json and "content" in response_json["message"]:
            answer = response_json["message"]["content"]
            filtered_answer = remove_think_tags(answer)
            save_to_file(output_file, filtered_answer)

            with open("content_log.txt", "a", encoding="utf-8") as file:
                file.write("小朋友 : ")
                file.write(document_content + "\n") 
                file.write("你的回答 : ")
                file.write(filtered_answer + "\n") 
                file.write("\n")  

            # 使用 edge-tts 中文男聲 語音合成與儲存
            yee+=1
            os.makedirs("audio_log", exist_ok=True)
            output_audio_path = rf"audio_log/output{yee}.mp3"
            speak_and_save(filtered_answer, filename=output_audio_path)
        else:
            print("API 回應格式異常：", response_json)
