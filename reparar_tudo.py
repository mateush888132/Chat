import os
import sys
from dotenv import load_dotenv

# Tenta carregar o .env
load_dotenv()

print("\n" + "="*40)
print("  DIAGNÓSTICO E REPARO DO CINEBOT")
print("="*40 + "\n")

# 1. VERIFICAÇÃO DAS CHAVES DE API
print("1. Verificando Chaves de API...")
google_key = os.getenv("GOOGLE_API_KEY")
tmdb_key = os.getenv("TMDB_API_KEY")

if not google_key:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada no arquivo .env!")
    print("   Sem isso, o chat não funciona.")
else:
    print(f"✅ GOOGLE_API_KEY encontrada: {google_key[:5]}...******")

if not tmdb_key:
    print("❌ ERRO: TMDB_API_KEY não encontrada no arquivo .env!")
    print("   Sem isso, as imagens dos filmes não carregam.")
else:
    print(f"✅ TMDB_API_KEY encontrada: {tmdb_key[:5]}...******")

if not google_key or not tmdb_key:
    print("\n🔴 PARE AQUI: Corrija o arquivo .env antes de continuar.")
    sys.exit()

# 2. TENTATIVA DE CONEXÃO COM O BANCO DE DADOS
print("\n2. Recriando o Banco de Dados...")
try:
    # Importa o app para ter acesso ao SQLAlchemy
    from chatbot import app, db, User
    
    # Força a criação do arquivo no disco
    db_path = os.path.join(os.getcwd(), 'cinebot.db')
    if os.path.exists(db_path):
        print(f"   Arquivo antigo encontrado. Removendo: {db_path}")
        os.remove(db_path)
    
    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Cria um usuário de teste para garantir que a escrita funciona
        if not User.query.filter_by(username='admin').first():
            # Apenas para testar se a tabela aceita os novos campos
            print("   Testando inserção de usuário...")
            # Nota: senha hashada '123' fictícia apenas para teste de DB
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(app)
            pw_hash = bcrypt.generate_password_hash('123').decode('utf-8')
            
            teste = User(
                username='admin', 
                email='admin@teste.com', 
                password_hash=pw_hash,
                bio='Perfil de teste',
                avatar_pos_x=50,
                avatar_pos_y=50
            )
            db.session.add(teste)
            db.session.commit()
            print("✅ Usuário de teste gravado com sucesso.")

    print(f"✅ Arquivo de banco criado em: {db_path}")

except Exception as e:
    print(f"❌ ERRO CRÍTICO AO CRIAR BANCO: {e}")
    print("   Verifique se o arquivo chatbot.py está salvo corretamente e sem erros de sintaxe.")
    sys.exit()

print("\n" + "="*40)
print("  TUDO PRONTO! AGORA FAÇA O SEGUINTE:")
print("="*40)
print("1. Feche este terminal.")
print("2. Abra um novo terminal.")
print("3. Rode: python chatbot.py")
print("4. No navegador, FAÇA LOGOUT e crie uma conta nova.")
print("========================================\n")