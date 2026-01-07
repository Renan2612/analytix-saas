import sqlite3
import streamlit_authenticator as stauth

def conectar():
    return sqlite3.connect('usuarios.db', check_same_thread=False)

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    # Criamos a tabela com as colunas de plano e contagem de uso
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (nome TEXT, email TEXT, username TEXT PRIMARY KEY, 
                  password TEXT, plano_ativo INTEGER DEFAULT 0,
                  contagem_analises INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, username, senha_plana):
    senha_hash = stauth.Hasher.hash(senha_plana)
    try:
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO usuarios (nome, email, username, password, plano_ativo, contagem_analises) VALUES (?, ?, ?, ?, 0, 0)", 
                  (nome, email, username, senha_hash))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")
        return False

def buscar_usuarios():
    criar_tabela()
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios")
    dados = c.fetchall()
    conn.close()
    
    credentials = {'usernames': {}}
    for d in dados:
        credentials['usernames'][d[2]] = {
            'name': d[0], 
            'password': d[3], 
            'email': d[1],
            'plano_ativo': d[4],
            'contagem_analises': d[5]
        }
    return credentials

def ativar_plano(username):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET plano_ativo = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def incrementar_analise(username):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET contagem_analises = contagem_analises + 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Inicializa o banco
criar_tabela()
