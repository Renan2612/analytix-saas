import streamlit as st
import database as db
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import timedelta

# Configuração da página
st.set_page_config(page_title="Analytix SaaS", layout="wide")

# Carregar usuários do bd
credenciais = db.buscar_usuarios()

authenticator = stauth.Authenticate(
    credenciais,
    "analytix_cookie", "chave_secreta_123", cookie_expiry_days=30
)

# MENU LATERAL: Login ou Cadastro
opcao = st.sidebar.selectbox("Menu", ["Login", "Cadastrar-se"])

if opcao == "Cadastrar-se":
    st.title("📝 Crie sua conta Analytix")
    with st.form("form_cadastro"):
        novo_nome = st.text_input("Nome Completo")
        novo_email = st.text_input("E-mail")
        novo_user = st.text_input("Escolha um Usuário")
        nova_senha = st.text_input("Senha", type="password")
        btn_cadastrar = st.form_submit_button("Finalizar Cadastro")
        
        if btn_cadastrar:
            if db.cadastrar_usuario(novo_nome, novo_email, novo_user, nova_senha):
                st.success("Cadastro realizado! Mude para o menu de Login.")
            else:
                st.error("Este usuário já existe.")

elif opcao == "Login":
    name, authentication_status, username = authenticator.login("Acesso ao Sistema", "main")

    if authentication_status:
        # --- ÁREA LOGADA
        authenticator.logout("Sair", "sidebar")
        st.title(f"📊 Bem-vindo, {name}")
        
        # DICA PARA O TEMA:
        st.info("💡 Para mudar para o Modo Claro/Escuro, vá ao menu (⋮) -> Settings -> Theme.")
        
        # Entra o código de upload e IA
        arquivo = st.sidebar.file_uploader("Anexe seu CSV", type="csv")
        if arquivo:
            st.write("Processando sua análise de alto padrão...")

    elif authentication_status is False:
        st.error("Usuário/Senha incorretos")
    elif authentication_status is None:
        st.warning("Por favor, insira suas credenciais.")