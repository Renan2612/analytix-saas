import sqlite3
import streamlit_authenticator as stauth

def conectar(): 
    return sqlite3.connect('usuarios.db')

def criar_tabela(): 
    conn = conectar()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                (nome TEXT, 
                email TEXT,
                username TEXT PRIMARY KEY, 
                password TEXT)''')
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, username, senha_plana): 
    senha_hash = stauth.Hasher([senha_plana]).generate()[0]
    try:
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", 
                  (nome, email, username, senha_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Usuário já existe

def obter_usuarios():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios")
    dados = c.fetchall()
    conn.close()
    
    # Organizar para o formato que o Authenticator precisa
    credencials = {'usernames': {}}
    for d in dados: 
        credencials['usernames'][d[2]] = {'name': d[0], 'password': d[3]}
    return credencials

#Inicializa o banco de dados para rodar o arquivo
criar_tabela()