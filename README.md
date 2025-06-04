# 🚀 Desafio Técnico - Engenheiro de Suporte

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

## 📋 Visão Geral

Este projeto resolve quatro desafios técnicos específicos de Engenharia de Suporte através de soluções automatizadas e análises detalhadas:

- 📊 **Análise de Dados**: Processamento automatizado de datasets com visualizações estatísticas
- 🔗 **Integração de Sistemas**: Automação de fluxos entre Make.com e Umbler Talk
- 🌐 **Auditoria Web**: Avaliação técnica de performance, SEO e acessibilidade
- 📧 **Diagnóstico de E-mail**: Análise de problemas de entrega e configuração DNS

### ✨ Características Técnicas

- Interface web responsiva desenvolvida com Tailwind CSS
- Scripts Python para análise estatística de grandes datasets
- Integração com Google Sheets API para manipulação de dados em tempo real
- Documentação técnica completa com diagramas de fluxo
- 11 gráficos especializados em formato WebP otimizado
- Aplicação PWA com Service Workers para uso offline

## 🏗️ Estrutura do Repositório

```text
├── 📁 assets/                    # 11 gráficos WebP otimizados (análises visuais)
├── 📁 diagrams/                  # Diagramas Mermaid para fluxos técnicos
├── 📁 google_api/               # API Google Sheets + credenciais + documentação
├── 📁 html/                     # 4 páginas web especializadas por seção
├── 📁 markdown/                 # Documentação markdown de cada desafio
├── 📁 scripts/                  # Script Python para análise de dados (597 linhas)
├── 📄 index.html               # Dashboard principal (885 linhas, PWA-ready)
├── 📄 package.json             # Configurações Node.js e scripts de automação
├── 📄 requirements.txt         # Dependências Python para análise de dados
└── 📄 README.md                # Esta documentação
```

### 📊 Assets de Análise de Dados

- `data_analysis_flow_sessao_2_analise_dados.webp` - Fluxograma da análise
- `grafico_*_sessao_2.webp` - 8 gráficos especializados (dispersão, distribuição, etc.)
- `fluxo_umler_talk.webp` - Fluxograma de integração Make.com

## 🚀 Instruções de Uso

### 📋 Pré-requisitos

- **Node.js** 16+ instalado
- **Python** 3.8+ instalado (testado com Python 3.13.3)
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)

### ⚡ Início Rápido

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/desafio-engenharia-suporte.git
   cd desafio-engenharia-suporte
   ```

2. **Instale as dependências Python:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Instale as dependências Node.js:**

   ```bash
   npm install
   ```

4. **Inicie o servidor de desenvolvimento:**

   ```bash
   npm run dev
   ```

5. **Acesse a aplicação:**
   - Abra `http://localhost:3000` no navegador
   - O dashboard principal será carregado automaticamente

### 🐍 Executando Análise de Dados

1. **Certifique-se de que as dependências Python estão instaladas:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Navegue para a pasta scripts:**

   ```bash
   cd scripts
   ```

3. **Execute o script de análise:**

   ```bash
   python analise_dados_sessao_2.py
   ```

4. **Verifique os resultados:**
   - Gráficos gerados na pasta `assets/`
   - Relatório detalhado em `resultados_analise_detalhada.txt`

### 🔧 Scripts Disponíveis

```json
{
  "dev": "Inicia servidor de desenvolvimento",
  "build": "Otimiza imagens e minifica arquivos",
  "test": "Executa testes Lighthouse e acessibilidade", 
  "deploy": "Deploy para GitHub Pages",
  "format": "Formata código com Prettier",
  "lint": "Analisa código com ESLint"
}
```

## 💡 Soluções Implementadas

### 📊 1. Sistema de Análise de Dados

- **Conexão Google Sheets**: Autenticação OAuth2 e leitura automatizada de planilhas
- **Processamento Estatístico**: Cálculo de médias, medianas, distribuições e correlações
- **Visualizações Gráficas**: Geração de 11 gráficos especializados (dispersão, barras, histogramas)
- **Relatórios Automáticos**: Identificação de padrões, produtos problemáticos e métricas de performance

### 🔗 2. Automação Make.com + Umbler Talk

- **Fluxo Automatizado**: Detecção e processamento de clientes em teste grátis
- **Triggers Configurados**: Monitoramento de eventos específicos no Umbler Talk
- **Logging Estruturado**: Registro automático de dados em planilhas com timestamp e metadados
- **Notificações**: Sistema de alertas integrado ao chat da plataforma

### 🌐 3. Auditoria Técnica de Sites

- **Análise de Performance**: Medição de Core Web Vitals e métricas de carregamento
- **Auditoria SEO**: Verificação de meta tags, estrutura semântica e sitemap.xml
- **Teste de Acessibilidade**: Conformidade com diretrizes WCAG 2.1
- **Revisão UX/UI**: Avaliação de padrões de design e experiência do usuário

### 📧 4. Diagnóstico de Infraestrutura de E-mail

- **Análise DNS**: Verificação de registros SPF, DKIM e DMARC
- **Troubleshooting de Headers**: Rastreamento de rotas e identificação de problemas de entrega
- **Relatório de Conformidade**: Avaliação de configurações de segurança de e-mail
- **Recomendações Técnicas**: Soluções específicas para problemas identificados

## 🔧 Especificações Técnicas

### 🏗️ Arquitetura do Sistema

#### 📊 **Módulo de Análise de Dados**

- Script Python com 597 linhas para processamento estatístico
- Integração Google Sheets API com autenticação OAuth2
- Geração automatizada de 11 visualizações em formato WebP
- Algoritmos para detecção de outliers e análise de correlação

#### 💻 **Interface Web**

- Dashboard responsivo com 885 linhas HTML
- Framework TailwindCSS para estilização moderna
- Progressive Web App (PWA) com Service Workers
- Otimização de performance com lazy loading

#### 🔗 **Sistema de Integração**

- Automação Make.com configurada com triggers específicos
- Fluxos documentados com diagramas Mermaid
- Error handling robusto para tratamento de exceções
- Logging estruturado com timestamp e metadados

#### 🌐 **Ferramentas de Auditoria**

- Scripts para análise de Core Web Vitals
- Verificação automatizada de SEO e acessibilidade
- Diagnóstico DNS para infraestrutura de e-mail
- Relatórios técnicos com recomendações específicas

### 📈 Tecnologias Utilizadas

- **Frontend**: HTML5, CSS3, JavaScript ES6+, TailwindCSS
- **Backend**: Python 3.8+, Google APIs
- **Automação**: Make.com, Webhooks
- **Visualização**: Matplotlib, Seaborn, Charts.js
- **Performance**: PWA, Service Workers, WebP

## 📝 Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
