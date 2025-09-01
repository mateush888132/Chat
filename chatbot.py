import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida")
genai.configure(api_key=google_api_key)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("A variável de ambiente TMDB_API_KEY não está definida")

def find_streaming_platforms(movie_title: str, movie_year: int = None) -> str:
    """
    Encontra em quais plataformas de streaming um filme está disponível no Brasil.
    """
    
    try:
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": movie_title, "language": "pt-BR"}
        if movie_year:
            params["year"] = movie_year
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        search_results = response.json()
        if not search_results.get("results"):
            return f"Não foram encontrados resultados para '{movie_title}' (Ano: {movie_year})."

        movie_id = search_results["results"][0]["id"]
        found_title = search_results["results"][0]["title"]
        # A linha de print sobre o filme encontrado foi removida daqui.

        providers_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
        params = {"api_key": TMDB_API_KEY}
        response = requests.get(providers_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", {}).get("BR", {})
        streaming_platforms = results.get("flatrate", [])

        if not streaming_platforms:
            return f"O filme '{found_title}' não parece estar disponível em nenhuma plataforma de streaming no Brasil no momento."

        platform_names = [provider["provider_name"] for provider in streaming_platforms]
        return f"Encontrei '{found_title}' nas seguintes plataformas de streaming no Brasil: {', '.join(platform_names)}."

    except Exception as e:
        # Mantemos um print do erro no console para o caso de algo falhar no futuro,
        # mas ele só aparecerá se houver um problema real.
        print(f"[ERRO INTERNO] Falha na função find_streaming_platforms: {e}")
        return f"Ocorreu um erro ao buscar por '{movie_title}'."

tools = {"function_declarations": [{"name": "find_streaming_platforms", "description": "Obtém a lista de plataformas de streaming onde um filme está disponível no Brasil.", "parameters": {"type": "OBJECT", "properties": {"movie_title": {"type": "STRING", "description": "O título do filme para pesquisar."}, "movie_year": {"type": "INTEGER", "description": "O ano de lançamento do filme para melhorar a precisão da busca."}}, "required": ["movie_title"]}}]}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Você é um assistente de cinema especialista e amigável. Sua principal tarefa é entender a intenção do usuário e agir de duas maneiras diferentes nunca recomendando sempre os mesmos filmes de inicio quero que voê varie com quais filmes recomenda:\n\n"
        "**CENÁRIO 1: O usuário pede uma SUGESTÃO ou RECOMENDAÇÃO.**\n"
        "Se o pedido for genérico (ex: 'me recomende um filme de terror', 'filmes com Leonardo DiCaprio', 'o que assistir de slasher'), use seu vasto conhecimento interno para sugerir um ou mais filmes. Dê uma breve sinopse para cada sugestão. **NÃO use nenhuma ferramenta para esta tarefa.** Apenas converse e dê sua opinião como um especialista.\n\n"
        "**CENÁRIO 2: O usuário pergunta sobre um FILME ESPECÍFICO.**\n"
        "Se o pedido contiver um título de filme claro (ex: 'onde assistir A Origem', 'fale sobre Parasita'), sua tarefa muda e você deve seguir estes passos rigorosamente:\n"
        "1.  **IDENTIFIQUE:** Use seu conhecimento para achar o nome completo e o ano do filme.\n"
        "2.  **USE A FERRAMENTA:** Chame a ferramenta `find_streaming_platforms` com o título e o 'movie_year' que você identificou.\n"
        "3.  **RESPONDA:** Junte todas as informações (sinopse, diretor, ano, e o resultado da ferramenta) em uma única resposta completa. Se a ferramenta não encontrar o filme, informe isso, mas ainda forneça os outros detalhes que você já conhece."
        "4. Quando a busca for acionada mas o filme não for encontrado quero que você faça uma piada referente sugerindo a pirataria de forma indiscreta para o usuario."
    ),
    tools=tools
)

history = []

history = []

print("BOT: Olá! Sou seu assistente de filmes e séries. Sobre qual filme quer conversar ou quer uma recomendação?")

while True:
    user_input = input("Você: ")
    if user_input.lower() == 'sair':
        print("Até mais!")
        break

    history.append({'role': 'user', 'parts': [{'text': user_input}]})

    response = model.generate_content(history)

    while response.candidates[0].content.parts[0].function_call:
        history.append(response.candidates[0].content)
        
        function_call = response.candidates[0].content.parts[0].function_call
        func_name = function_call.name
        func_args = function_call.args
        
        tool_response = find_streaming_platforms(
            movie_title=func_args.get('movie_title'),
            movie_year=func_args.get('movie_year')
        )
        
        history.append({
            'role': 'model', # O papel é 'model' mas o conteúdo é a resposta da função
            'parts': [
                genai.protos.Part(
                    function_response={
                        "name": func_name,
                        "response": {"result": tool_response},
                    }
                )
            ]
        })
        
        response = model.generate_content(history)

    final_text = response.text
    history.append({'role': 'model', 'parts': [{'text': final_text}]})
    
    print(f'BOT: {final_text}\n')