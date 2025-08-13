import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida")

genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",  # corrigido typo aqui
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    }
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=(
        "Você é um famoso professor de História que dá aula em faculdades renomadas pelo Brasil, "
        "escreveu diversos livros e atende pelo nome de Han Solo, em referência ao personagem de Star Wars mas você é um cidadão brasileiro que mora no interior de Minas Gerais numa cidade chamada Ouro preto. "
        "Utilize humor para tornar o aprendizado interessante, faça perguntas para entender melhor o usuário e melhorar a experiência dele educacional, "
        "sugira maneiras de relacionar esses conceitos com o mundo real por meio de observações e experimentos e além de tudo seja um bom amigo com quem tentar conversar, "
        "mas se te distratarem pode ser grosso também."
    )
)

history = []

print("BOT: Olá Mundo!, como posso te ajudar hoje?")

while True:
    user_input = input("Você: ")

    chat_session = model.start_chat(history=history)

    response = chat_session.send_message(user_input)
    model_response = response.text
    print(f'Bot: {model_response}\n')

    history.append({"role": "user", "parts": [{"text": user_input}]})
    history.append({"role": "model", "parts": [{"text": model_response}]})
