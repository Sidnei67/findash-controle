# database.py (Versão de Teste)
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # Tenta abrir e avisa se conseguir
    try:
        sheet = client.open("FinDash_DB").sheet1
        st.toast("✅ Conexão com Google Sheets bem sucedida!", icon="🚀")
        return sheet
    except Exception as e:
        st.error(
            f"❌ Erro Crítico: Não consegui abrir a planilha. Detalhe: {e}")
        return None


def init_db():
    sheet = conectar_google_sheets()
    if sheet:
        try:
            if not sheet.cell(1, 1).value:
                sheet.append_row(
                    ["Data", "Tipo", "Categoria", "Descricao", "Valor"])
        except Exception as e:
            st.error(f"Erro ao escrever cabeçalho: {e}")


def adicionar_transacao(data, tipo, categoria, descricao, valor):
    sheet = conectar_google_sheets()
    if sheet:
        try:
            sheet.append_row(
                [str(data), tipo, categoria, descricao, float(valor)])
            st.toast("Transação salva na nuvem!", icon="☁️")
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")


def obter_todas_transacoes():
    sheet = conectar_google_sheets()
    if sheet:
        return sheet.get_all_records()
    return []
