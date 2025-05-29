import gspread
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import locale
import os
import re
import traceback
from google.oauth2.service_account import Credentials
from datetime import datetime
import numpy as np # Importado para cálculos como IQR

# Configurações (ajuste conforme necessário)
# ATENÇÃO: Considere usar um caminho absoluto ou uma variável de ambiente para TOKEN_JSON para maior portabilidade.
TOKEN_JSON = '../google_api/gen-lang-client-0612410085-c85902466701.json' # Ou o caminho correto para o seu ficheiro
NOME_PLANILHA = 'data set' # Nome exato da sua planilha Google
ARQUIVO_SAIDA_RESULTADOS = 'resultados_analise_detalhada.txt'
ASSETS_DIR_NAME = 'assets_v2' # Nome da pasta para guardar os gráficos

TOP_N_PRODUTOS = 10
TOP_N_MOTIVOS = 5

# Escopos da API do Google
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Dicionário para armazenar os resultados da análise
resultados_analise = {}

# Configurar locale para português do Brasil para formatação de datas e números, se necessário
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
except locale.Error as e:
    print(f"Aviso: Não foi possível definir o locale para pt_BR.UTF-8. Usando locale padrão. Erro: {e}")

def limpar_nome_coluna(nome_coluna):
    """Remove caracteres especiais, quebras de linha e espaços extras dos nomes das colunas."""
    if not isinstance(nome_coluna, str):
        return "" # Retorna string vazia se não for string
    nome_coluna = re.sub(r'\n', ' ', nome_coluna)  # Substitui quebras de linha por espaço
    nome_coluna = re.sub(r'[^\w\s%()/\.-]', '', nome_coluna)  # Permite alfanuméricos, %, (), /, ., -
    nome_coluna = ' '.join(nome_coluna.split())  # Remove espaços extras
    return nome_coluna.strip().lower()  # Converte para minúsculas e remove espaços das pontas

def encontrar_coluna(df_cols, keywords, default_col_name=""):
    """Encontra a coluna mais provável com base em palavras-chave, priorizando correspondência exata."""
    cleaned_default_col_name = limpar_nome_coluna(default_col_name)
    
    for keyword in keywords:
        keyword_lower = limpar_nome_coluna(keyword) # Limpa também a keyword para consistência
        # Procura por correspondência exata primeiro (após limpeza)
        for col in df_cols: # df_cols já devem estar limpos
            if keyword_lower == col:
                return col
        # Procura por correspondência parcial se exata não for encontrada
        for col in df_cols:
            if keyword_lower in col:
                return col
    # Tenta o nome padrão limpo se nenhuma keyword corresponder
    if cleaned_default_col_name and cleaned_default_col_name in df_cols:
        return cleaned_default_col_name
    return None

def main():
    """Função principal para executar a análise de dados."""
    print("Iniciando análise de dados da planilha...")

    # Caminho absoluto para a pasta de assets
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório do script
    assets_dir = os.path.join(base_dir, '..', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    print(f"Os gráficos serão salvos em: {assets_dir}")

    try:
        # Autenticação e acesso à planilha
        creds = Credentials.from_service_account_file(TOKEN_JSON, scopes=SCOPES)
        gc = gspread.authorize(creds)
        doc = gc.open(NOME_PLANILHA)
        sheet = doc.sheet1
        dados = sheet.get_all_values()
        print(f"Planilha '{NOME_PLANILHA}' acessada com sucesso. Total de linhas lidas (incluindo cabeçalho): {len(dados)}")

        if not dados or len(dados) < 2: # Precisa de cabeçalho e pelo menos uma linha de dados
            print("A planilha está vazia ou contém apenas o cabeçalho. Não há dados para analisar.")
            return # Encerra a execução se não houver dados

        header = [limpar_nome_coluna(h) for h in dados[0]]
        rows = dados[1:]
        df = pd.DataFrame(rows, columns=header)
        print(f"DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas.")
        print(f"Colunas detectadas: {df.columns.tolist()}")

        # --- PREPARAÇÃO DAS COLUNAS ---
        print("\n=== PREPARAÇÃO E VALIDAÇÃO DAS COLUNAS ===")
        
        date_col_keywords = ['data de abertura do card', 'data de criação do card', 'data de criação', 'data', 'date created', 'timestamp', 'abertura']
        date_col = encontrar_coluna(df.columns, date_col_keywords, 'data de abertura do card')
        num_datas_invalidas = 0
        df_valid_dates = pd.DataFrame() 
        if date_col:
            print(f"Coluna de data identificada: '{date_col}'")
            original_date_count = len(df[date_col])
            
            nome_coluna_temp_datas = '_original_date_values_for_retry_temp' 
            df[nome_coluna_temp_datas] = df[date_col].copy() 
            
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            
            if original_date_count > 0 and (df[date_col].isnull().sum() / original_date_count) > 0.75:
                print(f"Muitas datas ({df[date_col].isnull().sum()} de {original_date_count}) nulas com dayfirst=True. Tentando formato padrão/americano...")
                df[date_col] = pd.to_datetime(df[nome_coluna_temp_datas], errors='coerce') 
            
            if nome_coluna_temp_datas in df.columns: 
                del df[nome_coluna_temp_datas] 

            num_datas_invalidas = df[date_col].isnull().sum()
            if num_datas_invalidas > 0:
                print(f"Aviso: {num_datas_invalidas} valores na coluna '{date_col}' não puderam ser convertidos para data e foram definidos como NaT.")
            
            df_valid_dates = df.dropna(subset=[date_col]).copy() 
            if not df_valid_dates.empty:
                 df_valid_dates['MesAno'] = df_valid_dates[date_col].dt.to_period('M')
            else:
                print(f"Aviso: Após tentativa de conversão de datas na coluna '{date_col}', não restaram datas válidas.")
        else:
            print(f"ERRO: Coluna de data não encontrada usando keywords: {date_col_keywords}. Análises dependentes de data serão puladas.")

        time_col_keywords = ['tempo até o card ser finalizado (h)', 'tempo finalizado', 'tempo de finalização', 'resolution time', 'tempo para finalizar (h)']
        time_col = encontrar_coluna(df.columns, time_col_keywords, 'tempo até o card ser finalizado (h)')
        valid_times = pd.Series(dtype=float)
        outliers_removidos_count_tempo_finalizacao = 0
        total_original_tempo_finalizacao = 0
        if time_col:
            print(f"Coluna de tempo de finalização identificada: '{time_col}'")
            df[time_col] = pd.to_numeric(df[time_col].astype(str).str.replace(',', '.', regex=False), errors='coerce')
            temp_valid_times = df[time_col].dropna()
            total_original_tempo_finalizacao = len(temp_valid_times)
            if not temp_valid_times.empty:
                Q1 = temp_valid_times.quantile(0.25)
                Q3 = temp_valid_times.quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    valid_times = temp_valid_times[(temp_valid_times >= lower_bound) & (temp_valid_times <= upper_bound)]
                else: 
                    valid_times = temp_valid_times.copy()
                
                outliers_removidos_count_tempo_finalizacao = len(temp_valid_times) - len(valid_times)
                print(f"{outliers_removidos_count_tempo_finalizacao} outliers removidos da coluna '{time_col}'. {len(valid_times)} valores restantes de {total_original_tempo_finalizacao} originais não nulos.")
            else:
                print(f"Coluna '{time_col}' não contém dados numéricos válidos após conversão.")
        else:
            print(f"AVISO: Coluna de tempo de finalização não encontrada. Análises relacionadas serão puladas.")

        priority_col_keywords = ['prioridade', 'priority']
        priority_col = encontrar_coluna(df.columns, priority_col_keywords, 'prioridade')
        if priority_col:
            print(f"Coluna de prioridade identificada: '{priority_col}'")
            df[priority_col] = df[priority_col].astype(str).str.strip().str.lower()
        else:
            print(f"AVISO: Coluna de prioridade não encontrada. Análises relacionadas serão puladas.")

        response_col_keywords = ['tempo de primeira resposta ao card (h)', 'tempo primeira resposta', 'first response time', 'tempo para primeira resposta (h)']
        response_col = encontrar_coluna(df.columns, response_col_keywords, 'tempo de primeira resposta ao card (h)')
        if response_col:
            print(f"Coluna de tempo de primeira resposta identificada: '{response_col}'")
            df[response_col] = pd.to_numeric(df[response_col].astype(str).str.replace(',', '.', regex=False), errors='coerce')
            if df[response_col].isnull().all() and len(df[response_col]) > 0 : 
                 print(f"AVISO: Coluna '{response_col}' não contém dados numéricos válidos após conversão (todos os valores são nulos ou não numéricos).")
        else:
            print(f"AVISO: Coluna de tempo de primeira resposta não encontrada. Análises relacionadas serão puladas.")
            
        product_col_keywords = ['produto', 'product', 'sistema']
        product_col_name = encontrar_coluna(df.columns, product_col_keywords, 'produto')
        product_counts = pd.Series(dtype=int)
        if product_col_name:
            print(f"Coluna de produto identificada: '{product_col_name}'")
            df_cleaned_product = df.dropna(subset=[product_col_name]).copy()
            df_cleaned_product[product_col_name] = df_cleaned_product[product_col_name].astype(str).str.strip()
            df_cleaned_product = df_cleaned_product[df_cleaned_product[product_col_name] != ''] 
            if not df_cleaned_product.empty:
                product_counts = df_cleaned_product[product_col_name].value_counts()
            else:
                print(f"Coluna '{product_col_name}' não contém dados válidos (não nulos e não vazios) após limpeza.")
        else:
            print(f"AVISO: Coluna de produto não encontrada. Análises relacionadas serão puladas.")

        reason_col_keywords = ['motivo da abertura do card', 'motivo do card', 'motivo', 'reason', 'problema', 'issue', 'descrição']
        reason_col_name = encontrar_coluna(df.columns, reason_col_keywords, 'motivo do card')
        reason_counts = pd.Series(dtype=int)
        if reason_col_name:
            print(f"Coluna de motivo/problema identificada: '{reason_col_name}'")
            df_cleaned_reason = df.dropna(subset=[reason_col_name]).copy()
            df_cleaned_reason[reason_col_name] = df_cleaned_reason[reason_col_name].astype(str).str.strip()
            df_cleaned_reason = df_cleaned_reason[df_cleaned_reason[reason_col_name] != ''] 
            if not df_cleaned_reason.empty:
                reason_counts = df_cleaned_reason[reason_col_name].value_counts()
            else:
                print(f"Coluna '{reason_col_name}' não contém dados válidos (não nulos e não vazios) após limpeza.")
        else:
            print(f"AVISO: Coluna de motivo/problema não encontrada. Análises relacionadas serão puladas.")

        # --- ANÁLISES E RESULTADOS ---

        print("\n=== 1. MÊS COM MAIOR NÚMERO DE INCIDENTES ===")
        incident_counts_by_month = pd.Series(dtype=int) 
        if date_col and not df_valid_dates.empty and 'MesAno' in df_valid_dates.columns:
            incident_counts_by_month = df_valid_dates['MesAno'].value_counts().sort_index()
            if not incident_counts_by_month.empty:
                top_month_period = incident_counts_by_month.idxmax()
                top_month_count = incident_counts_by_month.max()
                try:
                    top_month_name = top_month_period.strftime('%B de %Y')
                except AttributeError:
                    try:
                        top_month_name = pd.to_datetime(str(top_month_period)).strftime('%B de %Y')
                    except ValueError: 
                        top_month_name = str(top_month_period) 

                resultado_1 = f"{top_month_name}, com {top_month_count} incidentes."
                print(f"O mês com maior número de incidentes foi {resultado_1}")
                resultados_analise["mes_maior_incidentes"] = resultado_1
            else:
                msg = "Não foi possível calcular (sem dados de incidentes por mês após processamento de datas)."
                print(msg)
                resultados_analise["mes_maior_incidentes"] = msg
        else:
            msg = f"Não foi possível realizar a análise de incidentes por mês: coluna de data ('{date_col}') não encontrada, sem datas válidas ou 'MesAno' não pôde ser gerado."
            print(msg)
            resultados_analise["mes_maior_incidentes"] = msg
        
        print("\n=== 2. MEDIANA DO TEMPO DE FINALIZAÇÃO ===")
        mean_time_finalizacao = np.nan 
        std_time_finalizacao = np.nan  
        if time_col and not valid_times.empty:
            median_time = valid_times.median()
            mean_time_finalizacao = valid_times.mean() 
            std_time_finalizacao = valid_times.std() 
            resultado_2 = f"{median_time:.2f} horas (após remoção de {outliers_removidos_count_tempo_finalizacao} outliers de {total_original_tempo_finalizacao} valores não nulos)."
            print(f"A mediana do tempo de finalização dos cards é: {resultado_2}")
            resultados_analise["mediana_tempo_finalizacao"] = resultado_2
        elif time_col and valid_times.empty and total_original_tempo_finalizacao > 0: 
            msg = "Todos os valores de tempo de finalização foram considerados outliers ou inválidos após o filtro."
            print(msg)
            resultados_analise["mediana_tempo_finalizacao"] = msg
        else: 
            msg = f"Não foi possível calcular: coluna de tempo de finalização ('{time_col}') não encontrada ou sem dados numéricos válidos."
            print(msg)
            resultados_analise["mediana_tempo_finalizacao"] = msg

        print("\n=== 3. MEDIANA DO TEMPO DE PRIMEIRA RESPOSTA (CARDS PRIORITÁRIOS) ===")
        valid_priority_response_times = pd.Series(dtype=float) 
        if priority_col and response_col and (response_col in df.columns and df[response_col].notna().any()):
            priority_values_true = ['true', 'verdadeiro', '1', 'sim', 'yes', 'alta', 'high', 'crítico', 'urgente'] 
            
            df_copy_priority = df.copy() 
            df_copy_priority['is_priority'] = df_copy_priority[priority_col].isin(priority_values_true)
            priority_cards_df = df_copy_priority[df_copy_priority['is_priority']].copy()

            if not priority_cards_df.empty:
                print(f"Número de cards prioritários encontrados: {len(priority_cards_df)}")
                valid_priority_response_times = priority_cards_df[response_col].dropna() 
                if not valid_priority_response_times.empty:
                    median_priority_response_time = valid_priority_response_times.median()
                    resultado_3 = f"{median_priority_response_time:.2f} horas."
                    print(f"A mediana do tempo de primeira resposta para cards prioritários é: {resultado_3}")
                    resultados_analise["mediana_tempo_primeira_resposta_prioritarios"] = resultado_3
                else:
                    msg = "Não há dados válidos de tempo de primeira resposta para os cards prioritários filtrados (todos os valores são nulos ou não numéricos)."
                    print(msg)
                    resultados_analise["mediana_tempo_primeira_resposta_prioritarios"] = msg
            else:
                msg = "Nenhum card prioritário encontrado com os critérios especificados."
                print(msg)
                resultados_analise["mediana_tempo_primeira_resposta_prioritarios"] = msg
        else:
            msg_parts = []
            if not priority_col: msg_parts.append(f"coluna de prioridade (ex: '{priority_col_keywords[0]}')")
            if not response_col: msg_parts.append(f"coluna de tempo de primeira resposta (ex: '{response_col_keywords[0]}')")
            elif response_col in df.columns and not df[response_col].notna().any():
                msg_parts.append(f"coluna de tempo de primeira resposta ('{response_col}') não contém dados numéricos válidos")
            elif response_col not in df.columns: 
                 msg_parts.append("coluna de tempo de primeira resposta não foi identificada")

            if not msg_parts: msg_parts.append("condição inesperada para análise de tempo de resposta prioritário")
            
            msg = f"Não foi possível calcular mediana de tempo de primeira resposta prioritário: {', e '.join(msg_parts)}."
            print(msg)
            resultados_analise["mediana_tempo_primeira_resposta_prioritarios"] = msg
            
        print(f"\n=== 4. PRODUTO COM MAIOR RECORRÊNCIA DE INCIDENTES (TOP {TOP_N_PRODUTOS}) ===")
        if product_col_name and not product_counts.empty:
            top_product = product_counts.idxmax()
            top_count = product_counts.max()
            total_incidents_with_product = product_counts.sum() 
            percentage = (top_count / total_incidents_with_product) * 100 if total_incidents_with_product > 0 else 0
            
            resultado_4 = f"{top_product}, com {top_count} incidentes ({percentage:.2f}% do total de {total_incidents_with_product} incidentes com produto definido)."
            print(f"O produto com maior recorrência de incidentes é '{top_product}', com {top_count} incidentes.")
            resultados_analise["produto_maior_recorrencia"] = resultado_4
        else:
            msg = f"Não foi possível calcular: coluna de produto ('{product_col_name if product_col_name else 'Não identificada'}') não encontrada ou sem dados válidos."
            print(msg)
            resultados_analise["produto_maior_recorrencia"] = msg

        print(f"\n=== 5. PROBLEMA MAIS RECORRENTE (TOP {TOP_N_MOTIVOS}) ===")
        if reason_col_name and not reason_counts.empty:
            top_reason = reason_counts.idxmax()
            top_reason_count = reason_counts.max()
            resultado_5_problema = f"'{top_reason}', com {top_reason_count} ocorrências."
            print(f"O problema mais recorrente é {resultado_5_problema}")
            resultados_analise["problema_mais_recorrente"] = resultado_5_problema
        else:
            msg = f"Não foi possível calcular: coluna de motivo/problema ('{reason_col_name if reason_col_name else 'Não identificada'}') não encontrada ou sem dados válidos."
            print(msg)
            resultados_analise["problema_mais_recorrente"] = msg

        # --- GERAÇÃO DE GRÁFICOS DETALHADOS ---
        print("\n--- GERANDO GRÁFICOS ---")

        print("Gráfico 1: Incidentes por Mês")
        if date_col and not incident_counts_by_month.empty: 
            if len(incident_counts_by_month) >= 1: 
                fig, ax = plt.subplots(figsize=(max(10, len(incident_counts_by_month) * 0.8), 8)) 
                
                bar_labels = incident_counts_by_month.index.astype(str)
                bars = ax.bar(bar_labels, incident_counts_by_month.values, color='skyblue', edgecolor='black', alpha=0.8)
                ax.set_title(f'Número de Incidentes por Mês\nTotal de Meses Analisados: {len(incident_counts_by_month)}', fontsize=16, fontweight='bold')
                ax.set_xlabel('Mês/Ano', fontsize=14)
                ax.set_ylabel('Quantidade de Incidentes', fontsize=14)
                plt.xticks(rotation=45, ha='right', fontsize=10)
                plt.yticks(fontsize=10)
                
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * yval, f'{int(yval)}', ha='center', va='bottom', fontsize=9)

                if len(incident_counts_by_month) > 1 : 
                    mean_incidents = incident_counts_by_month.mean()
                    ax.axhline(mean_incidents, color='green', linestyle='--', linewidth=2, label=f'Média de Incidentes: {mean_incidents:.1f}')
                    
                    max_val_idx_period = incident_counts_by_month.idxmax() 
                    max_val = incident_counts_by_month.max()
                    try:
                        max_idx_pos = incident_counts_by_month.index.get_loc(max_val_idx_period)
                        bars[max_idx_pos].set_color('salmon') 
                        ax.annotate(f'Máximo: {max_val}\n({str(max_val_idx_period)})', 
                                    xy=(bars[max_idx_pos].get_x() + bars[max_idx_pos].get_width() / 2, max_val), 
                                    xytext=(0, 20), textcoords='offset points', 
                                    ha='center', color='red', fontsize=10, fontweight='bold',
                                    arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=6))
                    except Exception as e_annotate: 
                         print(f"Aviso: Não foi possível localizar/anotar o máximo {max_val_idx_period} no gráfico de incidentes. Erro: {e_annotate}")
                ax.legend(fontsize=12)
                ax.grid(axis='y', linestyle=':', alpha=0.7)
                plt.tight_layout()
                plt.savefig(os.path.join(assets_dir, 'grafico_incidentes_por_mes_sessao_2.png'))
                plt.close(fig)
                print("Gráfico 'grafico_incidentes_por_mes_sessao_2.png' gerado com sucesso.")
            else: 
                print("Dados insuficientes para gerar o gráfico de incidentes por mês (nenhum mês com dados).")
        else:
            print("Gráfico de incidentes por mês não gerado: coluna de data não encontrada, sem dados válidos ou 'MesAno' não pôde ser gerado.")

        print("\nGráfico 2: Distribuição do Tempo de Finalização")
        if time_col and not valid_times.empty:
            if len(valid_times) > 1: 
                fig, ax = plt.subplots(figsize=(12, 7))
                n_bins = min(20, max(5, int(len(valid_times)/5))) 
                n, hist_bins, patches = ax.hist(valid_times, bins=n_bins, color='cornflowerblue', edgecolor='black', alpha=0.85) # Renomeado para hist_bins
                
                median_val = valid_times.median()
                mean_val = mean_time_finalizacao 
                
                # Calcular um pequeno deslocamento para a linha da média
                offset = 0
                bin_width = 0 # Inicializar bin_width
                offset_percentage = 0.20 # 20% da largura de um bin
                if len(hist_bins) > 1 : # Garante que temos pelo menos um bin
                    bin_width = hist_bins[1] - hist_bins[0]
                    offset = bin_width * offset_percentage 
                
                # Plotar Mediana, tracejada, vermelha (na posição exata)
                ax.axvline(median_val, color='red', linestyle='--', linewidth=2.5, label=f'Mediana: {median_val:.2f} h', zorder=2)
                
                # Plotar Média como linha SÓLIDA, verde, DESLOCADA, com alguma transparência e zorder maior
                ax.axvline(mean_val + offset, color='green', linestyle='-', linewidth=2.0, 
                            label=f'Média: {mean_val:.2f} h (deslocada)', 
                            zorder=3, alpha=0.8) 
                
                # Adicionar uma pequena seta para indicar a posição original da média
                # Condição: se offset foi aplicado e a diferença original entre média e mediana é menor que um limiar (ex: 1.5x o offset)
                if offset > 0 and abs(mean_val - median_val) < (offset * 1.5) and bin_width > 0 : 
                     y_annotate_pos = ax.get_ylim()[1] * 0.98 
                     ax.annotate(f'{mean_val:.2f}', 
                                xy=(mean_val, y_annotate_pos), 
                                xytext=(mean_val + offset, y_annotate_pos), 
                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='green', shrinkB=5),
                                ha='center', va='bottom', color='green', fontsize=8, 
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="green", lw=0.5, alpha=0.7))
                
                ax.set_title(f'Distribuição do Tempo de Finalização dos Cards\n(Outliers Removidos: {outliers_removidos_count_tempo_finalizacao} / {total_original_tempo_finalizacao} originais não nulos)', fontsize=16, fontweight='bold')
                ax.set_xlabel('Tempo de Finalização (horas)', fontsize=14)
                ax.set_ylabel('Frequência (Número de Cards)', fontsize=14)
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=10)
                ax.legend(fontsize=12)
                ax.grid(axis='y', linestyle=':', alpha=0.7)
                
                std_dev_text = f"Std Dev: {std_time_finalizacao:.2f} h" if not np.isnan(std_time_finalizacao) else "Std Dev: N/A"
                info_text = (f"Dados exibidos após remoção de outliers usando IQR.\n"
                             f"Total de cards válidos: {len(valid_times)}\n"
                             f"{std_dev_text}")
                ax.text(0.98, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

                plt.tight_layout()
                plt.savefig(os.path.join(assets_dir, 'grafico_tempo_finalizacao_sessao_2.png'))
                plt.close(fig)
                print("Gráfico 'grafico_tempo_finalizacao_sessao_2.png' gerado com sucesso.")
            else:
                print("Dados insuficientes para gerar o gráfico de distribuição do tempo de finalização (menos de 2 pontos de dados).")
        else:
            print("Gráfico de tempo de finalização não gerado: coluna não encontrada, sem dados válidos ou todos os dados removidos como outliers.")

        print("\nGráfico 3: Proporção de Incidentes por Prioridade")
        if priority_col and priority_col in df.columns and df[priority_col].nunique() > 0 : 
            prioridade_counts_series = df[priority_col].value_counts()
            if not prioridade_counts_series.empty:
                # Mapeamento explícito para rótulos amigáveis
                label_map = {
                    'true': 'Prioritário',
                    'verdadeiro': 'Prioritário',
                    '1': 'Prioritário',
                    'sim': 'Prioritário',
                    'yes': 'Prioritário',
                    'alta': 'Prioritário',
                    'high': 'Prioritário',
                    'crítico': 'Prioritário',
                    'urgente': 'Prioritário',
                    'false': 'Não Prioritário',
                    'falso': 'Não Prioritário',
                    '0': 'Não Prioritário',
                    'não': 'Não Prioritário',
                    'no': 'Não Prioritário',
                    'baixa': 'Não Prioritário',
                    'normal': 'Não Prioritário',
                    'média': 'Não Prioritário',
                    'medium': 'Não Prioritário',
                }
                prioridade_counts_series = prioridade_counts_series.rename(index=lambda x: label_map.get(str(x).strip().lower(), str(x).capitalize()))
                fig, ax = plt.subplots(figsize=(10, 8))
                colors = ['#8fd19e', '#bdbdbd'] if set(prioridade_counts_series.index) == {'Prioritário', 'Não Prioritário'} else plt.cm.Pastel2(np.linspace(0, 1, len(prioridade_counts_series)))
                wedges, texts, autotexts = ax.pie(prioridade_counts_series, 
                                                  labels=prioridade_counts_series.index, 
                                                  autopct=lambda p: '{:.1f}%\n({:.0f})'.format(p, p * sum(prioridade_counts_series)/100) if p > 0 else '',
                                                  startangle=90, 
                                                  colors=colors,
                                                  pctdistance=0.80, 
                                                  labeldistance=1.1, 
                                                  wedgeprops={'edgecolor': 'grey', 'linewidth': 0.5})
                
                for text in texts: 
                    text.set_fontsize(11)
                for autotext in autotexts: 
                    autotext.set_fontsize(9)
                    autotext.set_color('black')
                    autotext.set_fontweight('bold')

                ax.set_title(f'Proporção de Incidentes por Prioridade\nTotal de Incidentes: {sum(prioridade_counts_series)}', fontsize=16, fontweight='bold')
                ax.axis('equal') 
                plt.tight_layout()
                plt.savefig(os.path.join(assets_dir, 'grafico_proporcao_prioridade_sessao_2.png'))
                plt.close(fig)
                print("Gráfico 'grafico_proporcao_prioridade_sessao_2.png' gerado com sucesso.")
            else:
                print("Dados insuficientes para gerar o gráfico de proporção de prioridade (sem categorias de prioridade preenchidas).")
        else:
            print("Gráfico de proporção de prioridade não gerado: coluna de prioridade não encontrada ou sem categorias distintas.")

        print(f"\nGráfico 4: Top {TOP_N_PRODUTOS} Produtos com Mais Incidentes")
        if product_col_name and not product_counts.empty:
            top_n_data_prod = product_counts.nlargest(TOP_N_PRODUTOS)
            if len(top_n_data_prod) > 0:
                fig, ax = plt.subplots(figsize=(max(10, len(top_n_data_prod) * 1.2), 8)) 
                bars = ax.bar(top_n_data_prod.index.astype(str), top_n_data_prod.values, color='mediumseagreen', edgecolor='black', alpha=0.8)
                ax.set_title(f'Top {min(TOP_N_PRODUTOS, len(top_n_data_prod))} Produtos com Mais Incidentes', fontsize=16, fontweight='bold')
                ax.set_xlabel('Produto', fontsize=14)
                ax.set_ylabel('Quantidade de Incidentes', fontsize=14)
                plt.xticks(rotation=45, ha='right', fontsize=10)
                plt.yticks(fontsize=10)

                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01 * yval, f'{int(yval)}', ha='center', va='bottom', fontsize=9)
                
                ax.grid(axis='y', linestyle=':', alpha=0.7)
                plt.tight_layout()
                plt.savefig(os.path.join(assets_dir, 'grafico_distribuicao_produtos_sessao_2.png'))
                plt.close(fig)
                print(f"Gráfico 'grafico_distribuicao_produtos_sessao_2.png' (Top {TOP_N_PRODUTOS}) gerado com sucesso.")
            else:
                print(f"Dados insuficientes para gerar o gráfico de Top {TOP_N_PRODUTOS} produtos (nenhum produto com contagem).")
        else:
            print(f"Gráfico de Top {TOP_N_PRODUTOS} produtos não gerado: coluna de produto não encontrada ou sem dados válidos.")

        print(f"\nGráfico 5: Top {TOP_N_MOTIVOS} Motivos de Abertura de Cards")
        if reason_col_name and not reason_counts.empty:
            top_n_data_reason = reason_counts.nlargest(TOP_N_MOTIVOS)
            if len(top_n_data_reason) > 0:
                fig, ax = plt.subplots(figsize=(max(10, len(top_n_data_reason) * 1.5) , 7)) 
                bars = ax.bar(top_n_data_reason.index.astype(str), top_n_data_reason.values, color='slateblue', edgecolor='black', alpha=0.8)
                ax.set_title(f'Top {min(TOP_N_MOTIVOS, len(top_n_data_reason))} Motivos de Abertura de Cards', fontsize=16, fontweight='bold')
                ax.set_xlabel('Motivo do Card', fontsize=14)
                ax.set_ylabel('Quantidade de Ocorrências', fontsize=14)
                plt.xticks(rotation=30, ha='right', fontsize=10) 
                plt.yticks(fontsize=10)

                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01 * yval, f'{int(yval)}', ha='center', va='bottom', fontsize=9)

                ax.grid(axis='y', linestyle=':', alpha=0.7)
                plt.tight_layout() 
                plt.savefig(os.path.join(assets_dir, 'grafico_top5_motivos_sessao_2.png'))
                plt.close(fig)
                print(f"Gráfico 'grafico_top5_motivos_sessao_2.png' (Top {TOP_N_MOTIVOS}) gerado com sucesso.")
            else:
                print(f"Dados insuficientes para gerar o gráfico de Top {TOP_N_MOTIVOS} motivos (nenhum motivo com contagem).")
        else:
            print(f"Gráfico de Top {TOP_N_MOTIVOS} motivos não gerado: coluna de motivo não encontrada ou sem dados válidos.")

        # --- ATUALIZAR RELATÓRIO COM ANÁLISE QUALITATIVA ---
        print(f"\nSalvando resultados da análise em '{ARQUIVO_SAIDA_RESULTADOS}'...")
        with open(ARQUIVO_SAIDA_RESULTADOS, 'w', encoding='utf-8') as f:
            f.write("=== RESULTADOS DA ANÁLISE DETALHADA DE DADOS ===\n")
            f.write(f"Data da Análise: {datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}\n")
            f.write(f"Planilha Analisada: {NOME_PLANILHA}\n\n")

            f.write(f"1. Mês com Maior Número de Incidentes: {resultados_analise.get('mes_maior_incidentes', 'N/A ou dados insuficientes')}\n")
            f.write(f"2. Mediana do Tempo de Finalização: {resultados_analise.get('mediana_tempo_finalizacao', 'N/A ou dados insuficientes')}\n")
            f.write(f"3. Mediana do Tempo de Primeira Resposta (Cards Prioritários): {resultados_analise.get('mediana_tempo_primeira_resposta_prioritarios', 'N/A ou dados insuficientes')}\n")
            f.write(f"4. Produto com Maior Recorrência de Incidentes: {resultados_analise.get('produto_maior_recorrencia', 'N/A ou dados insuficientes')}\n")
            f.write(f"5. Problema Mais Recorrente: {resultados_analise.get('problema_mais_recorrente', 'N/A ou dados insuficientes')}\n\n")
            
            f.write("=== ANÁLISE QUALITATIVA PRELIMINAR ===\n")
            f.write("- O mês com maior número de incidentes ({}) pode indicar sazonalidade, eventos específicos ou campanhas que impactaram o volume. Recomenda-se investigar as causas subjacentes a esse pico.\n".format(resultados_analise.get('mes_maior_incidentes', 'N/D')))
            f.write("- A mediana do tempo de finalização ({}) e de primeira resposta para prioridades ({}) são KPIs cruciais. Valores altos podem indicar gargalos no processo ou necessidade de mais recursos/treinamento.\n".format(resultados_analise.get('mediana_tempo_finalizacao', 'N/D'), resultados_analise.get('mediana_tempo_primeira_resposta_prioritarios', 'N/D')))
            f.write("- O produto com maior recorrência de incidentes ({}) deve ser um foco de atenção. Pode necessitar de melhorias, atualizações na documentação ou treinamento específico para a equipa de suporte e utilizadores.\n".format(resultados_analise.get('produto_maior_recorrencia', 'N/D')))
            f.write("- O problema mais recorrente ({}) sinaliza uma área crítica. Analisar a causa raiz e implementar soluções preventivas (ex: melhorias no produto, FAQs, tutoriais) pode reduzir significativamente o volume de chamados.\n\n".format(resultados_analise.get('problema_mais_recorrente', 'N/D')))
            
            f.write("=== ARQUIVOS DE GRÁFICOS GERADOS (na pasta '{}') ===\n".format(ASSETS_DIR_NAME))
            graficos_gerados_nomes = []
            if os.path.exists(os.path.join(assets_dir, 'grafico_incidentes_por_mes_sessao_2.png')): graficos_gerados_nomes.append('grafico_incidentes_por_mes_sessao_2.png')
            if os.path.exists(os.path.join(assets_dir, 'grafico_tempo_finalizacao_sessao_2.png')): graficos_gerados_nomes.append('grafico_tempo_finalizacao_sessao_2.png')
            if os.path.exists(os.path.join(assets_dir, 'grafico_proporcao_prioridade_sessao_2.png')): graficos_gerados_nomes.append('grafico_proporcao_prioridade_sessao_2.png')
            if os.path.exists(os.path.join(assets_dir, 'grafico_distribuicao_produtos_sessao_2.png')): graficos_gerados_nomes.append('grafico_distribuicao_produtos_sessao_2.png')
            if os.path.exists(os.path.join(assets_dir, 'grafico_top5_motivos_sessao_2.png')): graficos_gerados_nomes.append('grafico_top5_motivos_sessao_2.png')

            if graficos_gerados_nomes:
                for nome_grafico in graficos_gerados_nomes:
                    f.write(f"- {nome_grafico}\n")
            else:
                 f.write("(Nenhum gráfico principal gerado devido à falta de dados ou colunas, ou erro na geração.)\n")

        print(f"\nAnálise concluída. Resultados salvos em '{ARQUIVO_SAIDA_RESULTADOS}'.")
        print(f"Gráficos salvos na pasta: '{assets_dir}'")

    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de token '{TOKEN_JSON}' não foi encontrado. Verifique o caminho e as permissões.")
        traceback.print_exc()
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERRO CRÍTICO: A planilha '{NOME_PLANILHA}' não foi encontrada. Verifique o nome e se o acesso foi concedido à conta de serviço.")
        traceback.print_exc()
    except gspread.exceptions.APIError as e:
        print(f"ERRO CRÍTICO DE API DO GOOGLE: {e}. Verifique as permissões da API e da conta de serviço.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a análise: {e}")
        traceback.print_exc()
    finally:
        print("Encerrando o programa.")

if __name__ == '__main__':
    main()

# Para executar este script:
# 1. Certifique-se de ter as bibliotecas instaladas:
#    pip install gspread pandas matplotlib google-auth oauth2client numpy
# 2. Configure o caminho para o `TOKEN_JSON` corretamente.
# 3. Coloque o nome da sua planilha Google em `NOME_PLANILHA`.
# 4. Execute no terminal: python nome_do_seu_script.py