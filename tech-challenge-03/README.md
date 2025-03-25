Link do vídeo: https://www.youtube.com/watch?v=uAXB5pAIiTE

Link do repositório: https://github.com/carlos-rian/fiap-pos-tech/tree/main/tech-challenge-03

# Fine-Tuning para Modelos de Linguagem

## 📌 Objetivo do Código
Este código tem como finalidade realizar o pré-processamento de dados e a formatação adequada para o fine-tuning de um modelo de linguagem baseado em OpenAI. A aplicação extrai dados de um banco de dados PostgreSQL, filtra e organiza as informações e as transforma em um formato compatível para o treinamento do modelo.

---

## 📂 Estrutura do Código
O código é composto pelas seguintes etapas e funções principais:

### 📌 1. Definição de Configurações e Importação de Bibliotecas
- 📌 Importa módulos essenciais como `os`, `json`, `pathlib` e bibliotecas externas (`pysqlx_engine` para conexão com banco de dados e `openai` para interação com modelos de IA).
- 📌 Define caminhos para armazenamento dos arquivos de saída, incluindo:
  - 🗂 **`CLEAN_FILE`**: Contém os dados extraídos e filtrados do banco de dados.
  - 🗂 **`FINE_TUNING_FILE`**: Contém os dados formatados para o fine-tuning.

---

### 🔗 2. Conexão com o Banco de Dados
#### 🔹 Função: `get_database_connection()`
🔹 **Descrição:** Estabelece a conexão com o banco de dados PostgreSQL utilizando a biblioteca `pysqlx_engine`. Retorna um objeto de conexão ativo.

---

### 🔍 3. Extração e Limpeza de Dados
#### 🔹 Função: `save_clean_data()`
✅ **Descrição:**
- Executa uma consulta SQL que filtra registros do banco de dados.
- A consulta garante que:
  - O conteúdo tem mais de **10 caracteres**.
  - O título do produto é válido e **não está em branco**.
  - Apenas títulos com pelo menos **10 ocorrências** são selecionados.
- Os resultados são armazenados no arquivo `CLEAN_FILE` no formato JSON.

---

### 📑 4. Processamento e Formatação para Fine-Tuning
#### 🔹 Função: `generate_fine_tuning_data()`
✅ **Descrição:**
- Lê os dados do arquivo `CLEAN_FILE`.
- Para cada registro, estrutura os dados conforme o formato esperado pelo modelo OpenAI:
  - Cada entrada consiste em uma sequência de mensagens (`messages`) contendo:
    1️⃣ **Mensagem do sistema** (definindo o comportamento do assistente).
    2️⃣ **Entrada do usuário** (título do produto).
    3️⃣ **Resposta esperada do assistente** (descrição do produto).
- Os dados são armazenados no arquivo `FINE_TUNING_FILE` para posterior utilização no treinamento do modelo.

---

## 🔄 Fluxo de Dados
1️⃣ **Extração dos Dados:**
   - O código inicia conectando-se ao banco de dados PostgreSQL.
   - Executa uma consulta SQL que retorna um conjunto de títulos e descrições de produtos filtrados.
   - Os dados resultantes são armazenados no arquivo `CLEAN_FILE`.

2️⃣ **Pré-processamento e Formatação:**
   - O código lê os registros do `CLEAN_FILE` e os estrutura em um formato adequado para fine-tuning.
   - Cada entrada no arquivo de saída (`FINE_TUNING_FILE`) contém um contexto de conversação usado para treinar o modelo OpenAI.

3️⃣ **Saída Final:**
   - O arquivo `FINE_TUNING_FILE` gerado está pronto para ser utilizado no fine-tuning do modelo de linguagem.

---

## ▶️ Execução do Código
Para executar o código, basta rodar o script principal:
```bash
python fine_tuning.py
```
⚠️ **Certifique-se de que:**
- O banco de dados **PostgreSQL** está acessível.
- As credenciais de conexão estão **configuradas corretamente**.
- O diretório de saída (`files/`) possui **permissão de escrita**.

---

## 🎯 Conclusão
Este código automatiza o processo de **extração, filtragem e formatação de dados** para fine-tuning de um modelo de linguagem. O fluxo de processamento garante que os dados estejam organizados e padronizados antes de serem usados no treinamento, **maximizando a eficácia do modelo ajustado**.

