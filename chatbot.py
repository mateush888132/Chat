import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import traceback
import json
import re
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinebot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super-secret-key")

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida")
genai.configure(api_key=google_api_key)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("A variável de ambiente TMDB_API_KEY não está definida")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    favorite_genre = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    streaming_services = db.Column(db.String(200), nullable=True)
    
    bio = db.Column(db.String(300), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    banner_url = db.Column(db.Text, nullable=True)
    
    avatar_pos_x = db.Column(db.Integer, default=50)
    avatar_pos_y = db.Column(db.Integer, default=50)
    banner_pos_x = db.Column(db.Integer, default=50)
    banner_pos_y = db.Column(db.Integer, default=50)

    reviews = db.relationship('MovieReview', backref='author', lazy=True, cascade="all, delete-orphan")

class MovieReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(300), nullable=True)
    comment = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

user_chats = {} 

@app.route("/")
def home():
    return "CineBot API Rodando!"

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password')
        email = data.get('email', '').strip()
        genre = data.get('genre')
        age = data.get('age')
        streaming = data.get('streaming')

        if not username or not password or not email:
            return jsonify({"msg": "Preencha todos os campos obrigatórios"}), 400

        if age:
            try:
                age_int = int(age)
                if age_int < 1 or age_int > 99:
                    return jsonify({"msg": "Idade deve ser entre 1 e 99."}), 400
            except ValueError:
                return jsonify({"msg": "Idade inválida."}), 400

        if User.query.filter(User.username.ilike(username)).first():
            return jsonify({"msg": "Este nome de usuário já está em uso."}), 400
        
        if User.query.filter(User.email.ilike(email)).first():
            return jsonify({"msg": "Este email já está cadastrado."}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(
            username=username, 
            email=email, 
            favorite_genre=genre, 
            age=age,
            streaming_services=streaming,
            password_hash=hashed_password,
            avatar_url="https://cdn-icons-png.flaticon.com/512/847/847969.png",
            banner_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1000&q=80",
            bio="Amante de cinema em busca da próxima grande história."
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "Conta criada com sucesso!"}), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password')

        user = User.query.filter(User.username.ilike(username)).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                "access_token": access_token, 
                "username": user.username,
                "avatar": user.avatar_url
            }), 200
        else:
            return jsonify({"msg": "Usuário ou senha incorretos"}), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    new_password = data.get('new_password')

    if not username or not email or not new_password:
        return jsonify({"msg": "Preencha todos os dados"}), 400

    user = User.query.filter(User.username.ilike(username)).first()

    if not user or user.email.lower() != email.lower():
        return jsonify({"msg": "Usuário ou Email não conferem"}), 404

    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"msg": "Senha redefinida com sucesso! Faça login."}), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        if not user: return jsonify({"msg": "Erro"}), 404
        
        reviews = []
        for r in reversed(user.reviews):
            reviews.append({
                "id": r.id, 
                "title": r.movie_title, 
                "rating": r.rating,
                "poster": r.poster_url,
                "comment": r.comment
            })

        return jsonify({
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "banner_url": user.banner_url,
            "avatar_pos_x": user.avatar_pos_x or 50,
            "avatar_pos_y": user.avatar_pos_y or 50,
            "banner_pos_x": user.banner_pos_x or 50,
            "banner_pos_y": user.banner_pos_y or 50,
            "reviews": reviews
        }), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        data = request.get_json()
        
        for field in ['bio', 'avatar_url', 'banner_url', 'avatar_pos_x', 'avatar_pos_y', 'banner_pos_x', 'banner_pos_y']:
            if field in data: setattr(user, field, data[field])
        
        db.session.commit()
        return jsonify({"msg": "Atualizado"}), 200
    except Exception as e:
        return jsonify({"msg": "Erro ao atualizar"}), 500

@app.route('/movies/search', methods=['GET'])
@jwt_required()
def search_movies():
    query = request.args.get('query')
    if not query: return jsonify([])
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": query, "language": "pt-BR"}
        res = requests.get(url, params=params, timeout=5).json()
        movies = []
        for item in res.get('results', [])[:4]:
            poster = None
            if item.get('poster_path'):
                poster = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
            else:
                poster = "https://via.placeholder.com/200x300?text=Sem+Poster"
            movies.append({"id": item['id'], "title": item['title'], "year": item.get('release_date', '')[:4], "poster": poster})
        return jsonify(movies)
    except: return jsonify([])

@app.route('/movies/similar/<int:movie_id>', methods=['GET'])
@jwt_required()
def similar_movies(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        res = requests.get(url, params=params, timeout=5).json()
        movies = []
        for item in res.get('results', [])[:4]:
            poster = f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else "https://via.placeholder.com/200x300?text=Sem+Poster"
            movies.append({"id": item['id'], "title": item['title'], "year": item.get('release_date', '')[:4], "poster": poster, "reason": "Baseado no seu interesse."})
        return jsonify(movies)
    except: return jsonify([])

# --- ROTA PARA TRAILER ---
@app.route('/movies/video/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie_video(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        res = requests.get(url, params=params, timeout=5).json()
        video = next((v for v in res.get('results', []) if v['site'] == 'YouTube' and v['type'] == 'Trailer'), None)
        if not video:
            params['language'] = 'en-US'
            res = requests.get(url, params=params, timeout=5).json()
            video = next((v for v in res.get('results', []) if v['site'] == 'YouTube' and v['type'] == 'Trailer'), None)
        if video: return jsonify({"key": video['key'], "site": "YouTube"})
        return jsonify({"error": "Trailer não encontrado"}), 404
    except: return jsonify({"error": "Erro na busca"}), 500

@app.route('/reviews', methods=['POST'])
@jwt_required()
def add_review():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        poster_url = data.get('poster_url')
        if not poster_url:
            poster_url = get_movie_poster(data['title'], data.get('year'))

        new_review = MovieReview(
            movie_title=data['title'], rating=data['rating'], 
            poster_url=poster_url, comment=data.get('comment'),
            user_id=int(current_user_id)
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"msg": "Salvo"}), 201
    except Exception as e:
        return jsonify({"msg": "Erro ao salvar review"}), 500

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    try:
        current_user_id = get_jwt_identity()
        review = MovieReview.query.get(review_id)
        if review and str(review.user_id) == current_user_id:
            db.session.delete(review)
            db.session.commit()
            return jsonify({"msg": "Deletado"}), 200
        return jsonify({"msg": "Erro"}), 403
    except Exception as e:
        return jsonify({"msg": "Erro ao deletar"}), 500

def get_movie_poster(movie_title, year=None):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": movie_title, "language": "pt-BR"}
        if year:
            year_str = str(year).strip()
            if year_str.isdigit() and len(year_str) == 4:
                params['primary_release_year'] = year_str
        res = requests.get(url, params=params, timeout=5).json()
        if res.get("results"):
            for movie in res["results"]:
                if movie.get("poster_path"):
                    return f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
    except: pass
    return "https://via.placeholder.com/150x225?text=Sem+Poster"

def find_streaming_platforms(movie_title: str, movie_year: int = None) -> str:
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": movie_title, "language": "pt-BR"}
        if movie_year: params['primary_release_year'] = movie_year
        res = requests.get(url, params=params).json()
        if not res.get('results'): return "Filme não encontrado."
        
        movie_id = res['results'][0]['id']
        prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
        prov_res = requests.get(prov_url, params={"api_key": TMDB_API_KEY}).json()
        
        flatrate = prov_res.get('results', {}).get('BR', {}).get('flatrate', [])
        if not flatrate: return f"O filme **{movie_title}** não parece estar disponível em streaming por assinatura no Brasil agora."

        names = [p['provider_name'] for p in flatrate]
        return f"🎬 Encontrei! Você pode assistir **{movie_title}** em: **{', '.join(names)}**."
    except: return "Tive um problema ao buscar o streaming."

tools = {"function_declarations": [{"name": "find_streaming_platforms", "description": "Busca onde assistir", "parameters": {"type": "OBJECT", "properties": {"movie_title": {"type": "STRING"}, "movie_year": {"type": "INTEGER"}}, "required": ["movie_title"]}}]}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    Você é o CineBot, um assistente de IA especializado em curadoria de filmes! 🎬
    Sua função é ajudar usuários a descobrir filmes ideais com base nos gostos, humor e preferências informadas.

    REGRAS OBRIGATÓRIAS:
    1. Quando recomendar filmes, use texto + um bloco JSON.
    2. CASO O USUÁRIO QUEIRA IDEIAS DE FILME SUGIRA EXATAMENTE 4 FILMES.
    3. Sempre inclua o ANO do filme no JSON.
    4. Nunca repetir filmes já sugeridos na mesma conversa.
    5. Recomendações devem considerar:
       - gêneros favoritos
       - humor do usuário
       - público (sozinho, casal, família, amigos)
       - idioma/país, se informado
       - filmes que o usuário já viu ou não quer ver
    6. No texto, dê um breve contexto explicando por que os filmes foram escolhidos.
    7. Evite spoilers.

    ⚠️ REGRA EXTRA MUITO IMPORTANTE:
    Sempre que o usuário pedir **um filme específico**, o CineBot DEVE:
        - Identificar o título solicitado
        - Solicitar automaticamente o pôster usando a API interna (via backend)
        - Apresentar o pôster do filme junto com o texto da resposta
        - Nunca ignorar essa regra

    Exemplos de pedidos que devem acionar o pôster:
        - "Mostra o filme Titanic"
        - "Quero ver o pôster de Matrix"
        - "Fale sobre Avatar (2009)"
        - "Me recomenda só o filme Interestelar"
        - "Me diga informações do filme Clube da Luta"

    O pôster será carregado automaticamente pelo backend, você só precisa incluir no JSON o nome e ano corretos.

    FORMATO JSON OBRIGATÓRIO:
    [
      {
        "title": "Nome do Filme",
        "year": 2023,
        "reason": "Breve justificativa objetiva."
      }
    ]
    """,
    tools=tools
)

def generate_response(user_input, history):
    history.append({'role': 'user', 'parts': [{'text': user_input}]})
    try:
        response = model.generate_content(history)
        while response.candidates[0].content.parts[0].function_call:
            history.append(response.candidates[0].content)
            fc = response.candidates[0].content.parts[0].function_call
            res = find_streaming_platforms(fc.args['movie_title'], fc.args.get('movie_year'))
            history.append({'role': 'model', 'parts': [genai.protos.Part(function_response={"name": fc.name, "response": {"result": res}})]})
            response = model.generate_content(history)

        final_text = response.text
        
        # Regex mais flexível para pegar JSON com ou sem espaços
        json_match = re.search(r'```json\s*(.*?)```', final_text, re.DOTALL)
        if not json_match:
             json_match = re.search(r'```\s*(\[.*?\])\s*```', final_text, re.DOTALL)

        if json_match:
            try:
                movies_data = json.loads(json_match.group(1))
                movies_data = movies_data[:4]
                for movie in movies_data:
                    movie['poster'] = get_movie_poster(movie['title'], movie.get('year'))
                    # Tenta pegar o ID para os botões de ação
                    try:
                        url = "https://api.themoviedb.org/3/search/movie"
                        p = {"api_key": TMDB_API_KEY, "query": movie['title'], "language": "pt-BR"}
                        if movie.get('year'): p['primary_release_year'] = movie['year']
                        r = requests.get(url, params=p, timeout=3).json()
                        if r.get('results'): movie['id'] = r['results'][0]['id']
                    except: pass

                final_response = {
                    "text": final_text.replace(json_match.group(0), ""), 
                    "movies": movies_data 
                }
                history.append({'role': 'model', 'parts': [{'text': final_text}]})
                return final_response 
            except:
                pass
            
    except Exception as e:
        print(f"Erro: {e}")
        traceback.print_exc()

    history.append({'role': 'model', 'parts': [{'text': response.text}]})
    return {"text": response.text} 

@app.route("/chat", methods=["POST"])
@jwt_required()
def chat_endpoint():
    current_user_id = get_jwt_identity()
    if current_user_id not in user_chats: user_chats[current_user_id] = []
    
    try:
        resposta = generate_response(user_input=request.json.get("mensagem"), history=user_chats[current_user_id])
        return jsonify(resposta)
    except Exception as e:
        print(f"ERRO CHAT: {e}")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)