import os, random
import google.generativeai as genai
from pyrogram import Client, filters
import pyrogram
import json, time
import fitz  # PyMuPDF

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 5000,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction="Your name is Herculef Ai you are a telegram bot and you don't mention gemeni at all, you make multiple english MCQs with different questions from every text, 3 wrong answers and 1 right literal answer from the provided text, in json format  \\n[{\"question\":\"question\", 'options':['a1','a2','a3','a4'],'ans': 'ans' }]",
)

chat_session = model.start_chat(
  history=[]
)

print("Bot: Hi, how can I help you?\n")

app = Client("ola",
api_id=26913296,
api_hash='167aca8f46306b602d341d0c9d21a755',
bot_token="7682528688:AAEhVpPxNoy7pj3hoQBu_HxHY6az995nwD8")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("""يا مرحبا، هذا البوت اسمه هِرقل وهوَ لصناعة الـ MCQ 

لطفاً أرسل إلي بالطريقة إللي تعجبك :

- نص مكتوب
- ملف بصيغة PDF 

وحسويلك منّه كوز 🤍. """)
    print(f'{message.chat.first_name} started the bot')

@app.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("افتح أي ملزمة تحب،\n\n انسخ النص من الملزمة ثم ارسله هنا أو أرسل ملف PDF وححوله كوز\n - أيّ مشكلة تواجهك أبلغني لطفاً @flwlsbot 🤍!")
    print(f'{message.chat.first_name} asked for help')


@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.mime_type == "application/pdf":
        await message.reply(f"- انتظر لطفاً {message.chat.first_name}، ديحمّل الملف 🩵.")
        print(f"- انتظر لطفاً {message.chat.first_name}، ديحمّل الملف 🩵.")
        pdf_path = await message.download()
        text = extract_text_from_pdf(pdf_path)
        await process_text(client, message, text)
        os.remove(pdf_path)  # Delete the PDF file after processing


@app.on_message(filters.text)
async def handle_text(client, message):
    text = message.text
    print(f'{message.chat.first_name} : {text}')
    await process_text(client, message, text)

async def process_text(client, message, text):
    response = chat_session.send_message(text)
    model_response = json.loads(response.text)  # Parse the JSON response

    chat_session.history.append({"role": "user", "parts": [text]})
    chat_session.history.append({"role": "model", "parts": [response.text]})

    questions = model_response  # Assuming the response is a list of questions

    chat_id = message.chat.id
    for question_data in questions:
        question = question_data["question"]
        options = question_data["options"]
        ans = question_data["ans"]
        
        random.shuffle(options)
        correct_option_id = options.index(ans)  # Find the index of the correct answer

        await app.send_poll(
            chat_id,
            question=question,
            options=options,
            is_anonymous=True,
            type=pyrogram.enums.PollType.QUIZ,
            correct_option_id=correct_option_id)
        time.sleep(2)  # Add a delay between polls to avoid flooding

app.run()
