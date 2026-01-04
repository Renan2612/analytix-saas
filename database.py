import sqlite3
import streamlit_authenticator as stauth

def conectar():
    return sqlite3.connect('usuarios.db', check_same_thread=False)

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (nome TEXT, email TEXT, username TEXT PRIMARY KEY, 
                  password TEXT, plano_ativo INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def buscar_usuarios():
    # Garantimos que a tabela existe antes de buscar
    criar_tabela() 
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios")
    dados = c.fetchall()
    conn.close()
    
    credentials = {'usernames': {}}
    if dados:
        for d in dados:
            credentials['usernames'][d[2]] = {
                'name': d[0], 
                'password': d[3], 
                'email': d[1],
                'plano_ativo': d[4] 
            }
    return credentials

def cadastrar_usuario(nome, email, username, senha_plana):
    # Versão atualizada para streamlit-authenticator 0.3.0+
    # Agora usando o método estático hash() para uma única senha
    senha_hash = stauth.Hasher.hash(senha_plana)
    
    try:
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO usuarios (nome, email, username, password, plano_ativo) VALUES (?, ?, ?, ?, 0)", 
                  (nome, email, username, senha_hash))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")
        return False

def ativar_plano(username):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET plano_ativo = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Inicializa ao importar
criar_tabela()
