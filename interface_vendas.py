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

# Se o banco estiver vazio (primeiro acesso), criamos um dicionário padrão
if not credenciais['usernames']:
    credenciais = {'usernames': {}}
    
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
    # 1. Tenta realizar o Login
    authenticator.login(location='main')

    # 2. Se o login for um SUCESSO
    if st.session_state["authentication_status"]:
        username_atual = st.session_state["username"]
        nome_usuario = st.session_state["name"]
        
        # Busca dados atualizados do banco (para ver se ele já pagou)
        dados_user = db.buscar_usuarios()['usernames'][username_atual]
        
        st.sidebar.title(f"Olá, {nome_usuario}")
        authenticator.logout("Sair do Sistema", "sidebar")

        # --- VERIFICAÇÃO DE ASSINATURA ---
        if dados_user.get('plano_ativo') == 0:
            st.warning("⚠️ Sua conta gratuita não permite análises preditivas.")
            st.title("Assine o Plano Pro para Liberar a IA")
            
            # Aqui vai o link do seu Stripe
            st.link_button("💳 Assinar agora por R$ 99/mês", "https://buy.stripe.com/exemplo")
            
            if st.button("Simular Pagamento (DEBUG)"):
                db.ativar_plano(username_atual)
                st.rerun()
        else:
            # --- ÁREA LOGADA (PLANO ATIVO) ---
            st.success("💎 Assinatura Ativa - Acesso Premium")
            st.title(f"📊 Painel de Inteligência, {nome_usuario}")
            
            st.info("💡 Para mudar para o Modo Claro/Escuro, vá ao menu (⋮) -> Settings -> Theme.")
            
            arquivo = st.sidebar.file_uploader("Anexe seu CSV", type="csv")
            if arquivo:
                # AQUI VAI O SEU CÓDIGO DE MAPEAMENTO E IA QUE JÁ FIZEMOS
                st.write("Processando sua análise de alto padrão...")
                # (Insira aqui o código do LinearRegression e Plotly)

    # 3. Se o login FALHOU
    elif st.session_state["authentication_status"] is False:
        st.error("Usuário ou senha incorretos.")
        
    # 4. Se ele ainda NÃO TENTOU login
    elif st.session_state["authentication_status"] is None:
        st.warning("Por favor, insira suas credenciais.")
