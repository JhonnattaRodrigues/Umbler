# Google Sheets API - Guia Simplificado

> **OBSERVAÇÃO IMPORTANTE:** A conta Google usada e sua API, foram pessoais. A planilha foi hospedada em minha própria conta.

Este projeto permite conectar ao Google Sheets para ler e escrever dados nas suas planilhas do Google. É como usar Excel, mas tudo automatizado pelo código!

## O que você vai encontrar aqui

- [O que você precisa ter](#o-que-você-precisa-ter)
- [Passos para configurar no Google](#passos-para-configurar-no-google)
- [Como obter as chaves de acesso](#como-obter-as-chaves-de-acesso)
- [Como configurar no seu computador](#como-configurar-no-seu-computador)
- [Como usar o projeto](#como-usar-o-projeto)
- [Cuidados importantes](#cuidados-importantes)
- [Observações](#observações)

## O que você precisa ter

- Uma conta Google (gmail)
- Acesso à internet
- Python instalado no seu computador (versão 3.7 ou mais nova)
- Conhecimento básico de como usar o terminal/prompt de comando

## Passos para configurar no Google

Vamos configurar passo a passo, com imagens para facilitar:

1. Entre no [Google Cloud Console](https://console.cloud.google.com/) usando sua conta Google

2. Crie um novo projeto:
   - Clique no menu superior, onde mostra o nome do projeto atual
   - Clique em "Novo Projeto"
   - Dê um nome (exemplo: "Meu Projeto Planilhas")
   - Clique em "Criar"

3. Ative a API do Google Sheets:
   - No menu lateral, clique em "APIs e Serviços" > "Biblioteca"
   - Pesquise por "Google Sheets API"
   - Clique no resultado e depois em "Ativar"

4. Crie as credenciais:
   - No menu lateral, clique em "APIs e Serviços" > "Credenciais"
   - Clique em "Criar Credenciais" > "Conta de serviço"
   - Dê um nome para a conta (exemplo: "Conta Automação Planilhas")
   - Opcional: adicione uma descrição
   - Clique em "Criar e Continuar"
   - Na parte de permissões, selecione "Editor" (ou um papel mais restrito se souber o que está fazendo)
   - Clique em "Continuar" > "Concluir"

5. Baixe as credenciais:
   - Na lista de contas de serviço, clique nos três pontos da conta que criou
   - Selecione "Gerenciar chaves"
   - Clique em "Adicionar Chave" > "Criar nova chave"
   - Escolha o formato "JSON"
   - Clique em "Criar" - o arquivo será baixado automaticamente

## Como obter as chaves de acesso

1. Guarde o arquivo JSON baixado no passo anterior - ele contém suas chaves de acesso!
   - Renomeie para `credentials.json` para facilitar
   - Coloque-o na pasta do projeto (mesma pasta que os arquivos Python)

2. Compartilhe sua planilha:
   - Abra sua planilha no Google Sheets
   - Clique no botão "Compartilhar" no canto superior direito
   - Adicione o e-mail que está dentro do seu arquivo JSON
   - Dê permissão de "Editor"
   - Desmarque a opção "Notificar pessoas"
   - Clique em "Compartilhar"

## Como configurar no seu computador

1. Baixe este projeto:
   - Se você sabe usar Git: `git clone [URL-DO-REPOSITÓRIO]`
   - Ou baixe como ZIP e extraia para uma pasta

2. Instale o que é necessário:
   - Abra o terminal/prompt de comando
   - Navegue até a pasta do projeto
   - Execute:

   ```bash
   pip install -r requirements.txt
   ```

   Isso vai instalar todas as bibliotecas necessárias!

3. Coloque o arquivo de credenciais:
   - Certifique-se de que o arquivo `credentials.json` está na pasta do projeto

## Como usar o projeto

### Para iniciantes

1. Encontre o ID da sua planilha:
   - O ID está na URL quando você abre a planilha
   - Exemplo: `https://docs.google.com/spreadsheets/d/`**`1ABCDEfghIJKLMNOpqrsTUVwxYZ12345`**`/edit`
   - Neste exemplo, o ID é `1ABCDEfghIJKLMNOpqrsTUVwxYZ12345`

2. Edite o arquivo `connect_google_sheet.py`:
   - Abra o arquivo com qualquer editor de texto
   - Procure a linha que contém `SAMPLE_SPREADSHEET_ID`
   - Substitua o valor pelo ID da sua planilha
   - Salve o arquivo

3. Execute o script:
   - No terminal/prompt de comando, execute:

   ```bash
   python google_api/connect_google_sheet.py
   ```

4. Veja o resultado:
   - Se tudo der certo, você verá os dados da sua planilha no terminal
   - Se houver erros, leia a mensagem para entender o problema

### Exemplo prático

Se sua planilha tem dados de clientes, você pode:

- Ler todos os clientes automaticamente
- Adicionar novos clientes por código
- Atualizar informações em massa
- Exportar dados para outros formatos

Exemplo de código para ler dados:

```python
# Trecho de código para ler dados
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Página1!A1:E10").execute()
values = result.get('values', [])
for row in values:
    print(f"Nome: ANONIMO, Email: ANONIMO")
```

Exemplo para escrever dados:

```python
# Trecho de código para escrever dados
valores = [
    ["Nome Sobrenome", "email@anonimo.com", "00-00000-0000"],
]
body = {'values': valores}
result = sheet.values().update(
    spreadsheetId=SPREADSHEET_ID, range="Página1!A2:C3",
    valueInputOption="USER_ENTERED", body=body).execute()
```

## Cuidados importantes

- **NUNCA compartilhe seu arquivo de credenciais!** É como a senha do seu banco.
- Adicione `credentials.json` ao arquivo `.gitignore` se usar Git.
- Se o projeto não for mais usado, revogue o acesso da conta de serviço:
  - Abra sua planilha > Compartilhar > Clique no e-mail da conta de serviço > Remover

## Observações

- Se você está usando este código, precisará seguir os passos acima com sua própria conta Google.
- Dúvidas comuns:
  - "Erro de permissão": Verifique se compartilhou a planilha com o e-mail correto da conta de serviço
  - "API não ativada": Certifique-se de ter ativado a API Google Sheets para o projeto
  - "Arquivo não encontrado": Verifique o caminho do arquivo de credenciais

Para mais informações, consulte a [documentação oficial do Google Sheets API](https://developers.google.com/sheets/api/quickstart/python) ou entre em contato com o suporte técnico.
