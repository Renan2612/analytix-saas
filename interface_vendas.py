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

# Carregar usuários (do banco v2)
credenciais = db.buscar_usuarios()

if not credenciais['usernames']:
    credenciais = {'usernames': {}}
    
authenticator = stauth.Authenticate(
    credenciais,
    "analytix_cookie", "chave_secreta_123", cookie_expiry_days=30
)

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
                st.success("Cadastro realizado! Pode fazer login.")
            else:
                st.error("Usuário já existe.")

elif opcao == "Login":
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        username_logado = st.session_state["username"]
        nome_usuario = st.session_state["name"]
        
        # Busca fresca para ler o contador atualizado
        usuarios_db = db.buscar_usuarios()['usernames']
        user_info = usuarios_db.get(username_logado)

        if user_info:
            st.sidebar.title(f"👋 Olá, {nome_usuario}")
            authenticator.logout("Sair", "sidebar")

            status_plano = user_info.get('plano_ativo', 0)
            uso_atual = user_info.get('contagem_analises', 0)

            # Lógica de Permissão Freemium
            pode_acessar = False
            if status_plano == 1:
                pode_acessar = True
                st.sidebar.success("🚀 Plano Pro: Ilimitado")
            elif uso_atual < 3:
                pode_acessar = True
                st.sidebar.info(f"🎁 Grátis: {3 - uso_atual} restantes")
            else:
                pode_acessar = False

            if not pode_acessar:
                st.warning("⚠️ Limite gratuito atingido.")
                st.title("Assine o Plano Pro por R$ 79,90")
                col1, _ = st.columns(2)
                with col1:
                    st.info("- Análises Ilimitadas\n- IA Avançada")
                    st.link_button("💳 Assinar Agora", "https://buy.stripe.com/exemplo")
                if st.button("Simular Pagamento (DEBUG)"):
                    db.ativar_plano(username_logado)
                    st.rerun()
            else:
                # ÁREA LIBERADA
                st.title(f"📊 Painel Analytix: {nome_usuario}")
                arquivo = st.sidebar.file_uploader("📂 Anexe seu CSV", type="csv")
                
                if arquivo:
                    df_raw = pd.read_csv(arquivo)
                    colunas = df_raw.columns.tolist()
                    col_data = st.sidebar.selectbox("Coluna Data:", colunas)
                    col_vendas = st.sidebar.selectbox("Coluna Vendas:", colunas)

                    if st.sidebar.button("🚀 Gerar Dashboard"):
                        try:
                            # INCREMENTA O USO
                            db.incrementar_analise(username_logado)
                            
                            df = df_raw.copy().rename(columns={col_data: 'Data', col_vendas: 'Vendas'})
                            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
                            df = df.dropna(subset=['Data']).sort_values('Data')
                            df['Vendas'] = pd.to_numeric(df['Vendas'], errors='coerce')

                            # IA
                            df['Data_Ordinal'] = df['Data'].apply(lambda x: x.toordinal())
                            modelo = LinearRegression().fit(df[['Data_Ordinal']], df['Vendas'])
                            
                            ultima_data = df['Data'].max()
                            datas_futuras = [ultima_data + timedelta(days=i) for i in range(1, 31)]
                            previsoes = modelo.predict(np.array([d.toordinal() for d in datas_futuras]).reshape(-1, 1))

                            # Dash
                            st.markdown("---")
                            c1, c2 = st.columns(2)
                            c1.metric("Total Histórico", f"R$ {df['Vendas'].sum():,.2f}")
                            c2.metric("Projeção 30 dias", f"R$ {previsoes.sum():,.2f}")

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=df['Data'], y=df['Vendas'], name="Real"))
                            fig.add_trace(go.Scatter(x=datas_futuras, y=previsoes, name="IA", line=dict(dash='dash')))
                            fig.update_layout(template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.success("Análise contabilizada! Clique novamente em 'Gerar' para atualizar o contador.")
                        except Exception as e:
                            st.error(f"Erro: {e}")

    elif st.session_state["authentication_status"] is False:
        st.error("Login inválido")
    elif st.session_state["authentication_status"] is None:
        st.warning("Faça login.")
