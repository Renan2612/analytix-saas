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

    if st.session_state["authentication_status"]:
        username_atual = st.session_state["username"]
        nome_usuario = st.session_state["name"]
        
        # BUSCA DINÂMICA: Recarregamos do banco para garantir que o usuário novo seja encontrado
        todas_credenciais = db.buscar_usuarios()
        
        # Verificação de segurança para evitar o KeyError
        if username_atual in todas_credenciais['usernames']:
            dados_user = todas_credenciais['usernames'][username_atual]
            
            st.sidebar.title(f"Olá, {nome_usuario}")
            authenticator.logout("Sair do Sistema", "sidebar")

            # --- VERIFICAÇÃO DE ASSINATURA ---
            if dados_user.get('plano_ativo') == 0:
                st.warning("⚠️ Sua conta gratuita não permite análises preditivas.")
                st.title("Assine o Plano Pro para Liberar a IA")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**O que você terá no Plano Pro:**\n- IA Preditiva\n- Dashboards Interativos\n- Suporte VIP")
                    st.link_button("💳 Assinar agora por R$ 99/mês", "https://buy.stripe.com/exemplo")
                
                if st.button("Simular Pagamento com Sucesso (DEBUG)"):
                    db.ativar_plano(username_atual)
                    st.success("Pagamento confirmado! Reiniciando...")
                    st.rerun()
            else:
                # --- ÁREA PREMIUM LIBERADA ---
                st.success("💎 Acesso Premium Liberado")
                st.title(f"📊 Painel de Inteligência, {nome_usuario}")
                
                arquivo = st.sidebar.file_uploader("📂 1. Anexe seu arquivo CSV", type="csv")
                
                if arquivo:
                    # [AQUI CONTINUA O SEU CÓDIGO DE IA E GRÁFICOS]
                    st.write("Configurando mapeamento de colunas...")
                    # ... (restante do código de mapeamento e Plotly)
        else:
            st.error("Erro ao sincronizar dados. Por favor, tente recarregar a página.")

    elif st.session_state["authentication_status"] is False:
        st.error("Usuário ou senha incorretos.")
    elif st.session_state["authentication_status"] is None:
        st.warning("Por favor, faça login para acessar o software.")
