import streamlit as st
import database as db
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import timedelta

# 1. Configuração da página
st.set_page_config(page_title="Analytix SaaS", layout="wide")

# 2. Gestão de Autenticação
credenciais = db.buscar_usuarios()

if not credenciais['usernames']:
    credenciais = {'usernames': {}}
    
authenticator = stauth.Authenticate(
    credenciais,
    "analytix_cookie", "chave_secreta_123", cookie_expiry_days=30
)

# MENU LATERAL
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
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        username_logado = st.session_state["username"]
        nome_usuario = st.session_state["name"]
        
        # Busca fresca dos dados do usuário
        usuarios_db = db.buscar_usuarios()['usernames']
        user_info = usuarios_db.get(username_logado)

        if user_info:
            st.sidebar.title(f"👋 Olá, {nome_usuario}")
            authenticator.logout("Sair do Sistema", "sidebar")

            status_plano = user_info.get('plano_ativo', 0)
            uso_atual = user_info.get('contagem_analises', 0)

            # Lógica de Permissão
            pode_acessar = False
            if status_plano == 1:
                pode_acessar = True
                st.sidebar.success("🚀 Plano Pro: Ilimitado")
            elif uso_atual < 3:
                pode_acessar = True
                st.sidebar.info(f"🎁 Grátis: {3 - uso_atual} análises restantes")
            else:
                pode_acessar = False

            if not pode_acessar:
                st.warning("⚠️ Limite atingido! Você já realizou suas 3 análises gratuitas.")
                st.title("Assine o Plano Pro por R$ 79,90/mês")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**Vantagens do Pro:**\n- Análises Ilimitadas\n- Inteligência Artificial Avançada\n- Mapeamento de qualquer CSV")
                    st.link_button("💳 Assinar Plano Pro", "https://buy.stripe.com/exemplo")
                
                if st.button("Simular Pagamento (DEBUG)"):
                    db.ativar_plano(username_logado)
                    st.balloons()
                    st.rerun()
            else:
                # --- ÁREA DE TRABALHO LIBERADA ---
                st.title(f"📊 Painel Analytix: {nome_usuario}")
                arquivo = st.sidebar.file_uploader("📂 Anexe seu histórico CSV", type="csv")
                
                if arquivo:
                    df_raw = pd.read_csv(arquivo)
                    colunas = df_raw.columns.tolist()

                    st.sidebar.subheader("⚙️ Configurar Dashboard")
                    col_data = st.sidebar.selectbox("Coluna de Data:", colunas)
                    col_vendas = st.sidebar.selectbox("Coluna de Vendas:", colunas)

                    if st.sidebar.button("🚀 Gerar Dashboard Inteligente"):
                        try:
                            # Incrementa o uso no banco de dados
                            db.incrementar_analise(username_logado)
                            
                            # Processamento dos Dados
                            df = df_raw.copy()
                            df = df.rename(columns={col_data: 'Data', col_vendas: 'Vendas'})
                            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
                            df = df.dropna(subset=['Data']).sort_values('Data')
                            df['Vendas'] = pd.to_numeric(df['Vendas'], errors='coerce')

                            # IA: Regressão Linear
                            df['Data_Ordinal'] = df['Data'].apply(lambda x: x.toordinal())
                            modelo = LinearRegression().fit(df[['Data_Ordinal']], df['Vendas'])
                            
                            ultima_data = df['Data'].max()
                            datas_futuras = [ultima_data + timedelta(days=i) for i in range(1, 31)]
                            futuro_ord = np.array([d.toordinal() for d in datas_futuras]).reshape(-1, 1)
                            previsoes = modelo.predict(futuro_ord)

                            # Dashboard Visual
                            st.markdown("---")
                            c1, c2 = st.columns(2)
                            c1.metric("Faturamento Histórico", f"R$ {df['Vendas'].sum():,.2f}")
                            c2.metric("Projeção 30 dias", f"R$ {previsoes.sum():,.2f}")

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=df['Data'], y=df['Vendas'], name="Real", line=dict(color='#00d1b2')))
                            fig.add_trace(go.Scatter(x=datas_futuras, y=previsoes, name="IA", line=dict(color='#ff3860', dash='dash')))
                            fig.update_layout(template="plotly_dark", title="Tendência de Vendas")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.success("🤖 Análise concluída! O contador de uso foi atualizado.")
                            # Força atualização do contador na barra lateral no próximo clique
                        except Exception as e:
                            st.error(f"Erro no processamento: {e}")
                else:
                    st.info("👋 Aguardando upload do arquivo CSV.")

    elif st.session_state["authentication_status"] is False:
        st.error("Usuário ou senha incorretos.")
    elif st.session_state["authentication_status"] is None:
        st.warning("Por favor, faça login para acessar o software.")
