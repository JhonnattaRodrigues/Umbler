import gspread
from google.oauth2.service_account import Credentials
import os

# Caminho para o arquivo de credenciais JSON
# (ANONIMIZADO) Caminho para o arquivo de credenciais removido para LGPD
# token_json removido

# Nome da planilha (como aparece no Google Sheets)
nome_planilha = 'planilha_anonima'  # Nome anonimizado

# Escopos necessários
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Autenticação
# creds = Credentials.from_service_account_file(token_json, scopes=scopes)
# gc = gspread.authorize(creds)
# Abrir a planilha
# doc = gc.open(nome_planilha)
# Selecionar a primeira aba (worksheet)
# sheet = doc.sheet1
# Ler todas as linhas
# dados = sheet.get_all_values()
# Exibir os dados
# for linha in dados:
#     print(linha)
# Código de autenticação e acesso removido para anonimização LGPD
