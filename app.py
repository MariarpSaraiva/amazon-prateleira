import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timezone
import os
import re
from sqlalchemy import create_engine

# -----------------------------
# Configurações do Selenium
# -----------------------------
options = Options()
options.headless = True
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# -----------------------------
# URLs das categorias
# -----------------------------
urls_prateleira = {
    "https://www.amazon.com.br/s?k=m%C3%A1quina+de+lavar+roupa&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss": "Lavadoras e Secadoras",
    "https://www.amazon.com.br/s?k=Ferramentas&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss": "Ferramentas",
    "https://www.amazon.com.br/s?k=celular&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=K8ZQ80DAN3Q8&sprefix=celular%2Caps%2C261&ref=nb_sb_noss_1": "Celulares",
    "https://www.amazon.com.br/s?k=notebook&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=V42DVZPKYWI1&sprefix=notebooks%2Caps%2C223&ref=nb_sb_noss_1": "Notebook",
    "https://www.amazon.com.br/s?k=console&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss": "Videogames",
}

# -----------------------------
# Função para extrair informações
# -----------------------------
def extract_info(url, max_items=20, xpath_product="//div[@data-component-type='s-search-result']"):
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_product))
        )
    except Exception as e:
        print(f"Erro ao carregar a página: {e}")
        return pd.DataFrame()

    products = driver.find_elements(By.XPATH, xpath_product)
    data = []

    for i, product in enumerate(products):
        if i >= max_items:
            break

        title = "N/A"
        price = None
        asin = "N/A"

        # Extrair título
        try:
            title = product.find_element(By.CSS_SELECTOR, "div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1").text.strip()
        except:
            try:
                title = product.find_element(By.CSS_SELECTOR, "h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal").text.strip()
            except:
                try:
                    title = product.find_element(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal").text.strip()
                except:
                    pass

        if not title.strip():
            title = "N/A"

        # Extrair preço
        try:
            price_whole = product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
            price_fraction = product.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
            price_whole = re.sub(r"[^\d]", "", price_whole)
            price_fraction = re.sub(r"[^\d]", "", price_fraction)
            price = float(f"{price_whole}.{price_fraction}")
        except:
            try:
                price_text = product.find_element(By.CSS_SELECTOR, "span._cDEzb_p13n-sc-price_3mJ9Z").text.strip()
                price_text = re.sub(r"[^\d,]", "", price_text)
                price = float(price_text.replace(",", "."))
            except:
                price = None

        # Extrair ASIN
        try:
            asin = product.get_attribute("data-asin")
        except:
            pass
        if not asin or not re.match(r"^[A-Z0-9]{10}$", asin):
            try:
                link = product.find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")
                asin = re.search(r"/([A-Z0-9]{10})/", link).group(1)
            except:
                pass

        data.append({
            "produto": title,
            "preco": price,
            "data_hora": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "posicao": i + 1,
            "asin": asin,
        })

    return pd.DataFrame(data)

# -----------------------------
# Função para enviar DataFrame para banco
# -----------------------------
def send_to_database(df, table_name, db_type='sqlite', db_name='produtos.db',
                     user=None, password=None, host=None, port=None, if_exists='replace'):
    if db_type == 'sqlite':
        engine = create_engine(f'sqlite:///{db_name}')
    elif db_type == 'postgresql':
        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')
    elif db_type == 'mysql':
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}')
    else:
        raise ValueError("Tipo de banco não suportado")

    try:
        df.to_sql(table_name, engine, index=False, if_exists=if_exists)
        print(f"Dados gravados na tabela '{table_name}' do banco '{db_name}'")
    except Exception as e:
        print(f"Erro ao enviar dados para o banco: {e}")

# -----------------------------
# Função para salvar histórico
# -----------------------------
def save_with_history(df, category):
    if not os.path.exists("historico_produtos"):
        os.makedirs("historico_produtos")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df['data_hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(f"historico_produtos/{category}_{timestamp}.csv", index=False)

# -----------------------------
# Função para deletar CSV
# -----------------------------
def delete_csv_files():
    for file in os.listdir():
        if file.endswith(".csv"):
            os.remove(file)

# -----------------------------
# Loop principal
# -----------------------------
if __name__ == "__main__":
    while True:
        # Extração de prateleira
        dataframes_prateleira = {}
        for url, name in urls_prateleira.items():
            print(f"Extraindo dados para a categoria: {name}")
            df = extract_info(url)
            dataframes_prateleira[name] = df
            time.sleep(4)

        for category, df in dataframes_prateleira.items():
            csv_file = f"{category}_prateleira.csv"
            df.to_csv(csv_file, index=False)
            save_with_history(df, category)
            send_to_database(df, table_name=f"{category}_prateleira", db_type='sqlite', db_name='produtos.db', if_exists='replace')

        delete_csv_files()
        print("Aguardando 30 minutos antes da próxima execução...")
        time.sleep(1800)

driver.quit()
