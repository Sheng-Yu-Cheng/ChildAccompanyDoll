import pyttsx3
 
def speak(txt):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)
    engine.say(txt)
    engine.runAndWait()

speak("wahaha，lin-yu-an，林佑安不是高叉魔王，i love high fork!")