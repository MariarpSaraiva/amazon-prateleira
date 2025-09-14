# Web Scraper de Produtos da Amazon

Este projeto automatiza a coleta de informações de produtos da Amazon Brasil utilizando Selenium e Python.  
Os dados extraídos são armazenados em arquivos CSV e em um banco de dados relacional (SQLite, PostgreSQL ou MySQL).  

## Funcionalidades

- Extração de informações de diferentes categorias de produtos na Amazon:
  - Lavadoras e Secadoras
  - Ferramentas
  - Celulares
  - Notebooks
  - Videogames
- Captura automática de:
  - Nome do produto
  - Preço
  - Posição na prateleira
  - ASIN (código único da Amazon)
  - Data e hora da coleta
- Armazenamento em:
  - CSV temporário
  - Histórico de CSVs com timestamp
  - Banco de dados (SQLite por padrão)
- Rotina automatizada de atualização a cada 30 minutos
- Função para limpeza automática dos CSVs temporários

## Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Selenium](https://www.selenium.dev/)
- [Pandas](https://pandas.pydata.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/) (padrão, mas suporta PostgreSQL e MySQL)
- [webdriver-manager](https://pypi.org/project/webdriver-manager/)

## Instalação

Clone este repositório e instale as dependências:

```bash
git clone https://github.com/seuusuario/seurepositorio.git
cd seurepositorio
pip install -r requirements.txt
Se preferir instalar manualmente:

bash
Copiar código
pip install pandas selenium sqlalchemy webdriver-manager psycopg2-binary pymysql
Como Executar
bash
Copiar código
python scraper.py
O script irá:

Acessar os links de cada categoria.

Extrair as informações.

Salvar os dados em CSV e no banco produtos.db.

Guardar uma cópia no diretório historico_produtos/.

Repetir o processo a cada 30 minutos.

Banco de Dados
Por padrão, os dados são salvos em SQLite (produtos.db).
Para usar outro banco, ajuste os parâmetros da função send_to_database():

python
Copiar código
send_to_database(df, table_name="minha_tabela", db_type="postgresql",
                 db_name="meubanco", user="usuario", password="senha",
                 host="localhost", port=5432)
Bancos suportados:

SQLite

PostgreSQL

MySQL

Estrutura dos Dados
Cada registro contém:

Campo	Descrição
produto	Nome do produto
preco	Preço do produto (float)
data_hora	Data e hora da coleta
posicao	Posição na listagem
asin	Código ASIN da Amazon

Observações
O scraper roda em modo headless (sem abrir janela do navegador).

A Amazon pode alterar o layout de sua página, exigindo ajustes nos seletores.

Evite reduzir o tempo entre as requisições para não ser bloqueado.

yaml
Copiar código

---

## 📦 requirements.txt  

```markdown
pandas
selenium
sqlalchemy
webdriver-manager
psycopg2-binary
pymysql
