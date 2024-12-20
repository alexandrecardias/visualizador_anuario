import streamlit as st
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin  # Garantir URLs absolutas
import pandas as pd
import re  # Para manipular os títulos

# URLs principais organizadas por ano e em sequência numérica
URLS_BY_YEAR = {
    "2020": {
        "Geral": "https://anuario-estatistico-unb-2020.netlify.app/geral",
        "Graduação": "https://anuario-estatistico-unb-2020.netlify.app/grad",
        "Pós-Graduação": "https://anuario-estatistico-unb-2020.netlify.app/pos",
        "Mestrado": "https://anuario-estatistico-unb-2020.netlify.app/mest",
        "Doutorado": "https://anuario-estatistico-unb-2020.netlify.app/dout",
        "Produção Intelectual e Pesquisa": "https://anuario-estatistico-unb-2020.netlify.app/pip",
        "Extensão": "https://anuario-estatistico-unb-2020.netlify.app/ext",
        "Recursos Humanos": "https://anuario-estatistico-unb-2020.netlify.app/rh",
        "Atividades Comunitárias": "https://anuario-estatistico-unb-2020.netlify.app/comu",
        "Órgãos Complementares, Centros, Assessorias, Secretarias e Unidades Auxiliares": "https://anuario-estatistico-unb-2020.netlify.app/org",
        "Planejamento, Execução Orçamentária e Convênios": "https://anuario-estatistico-unb-2020.netlify.app/dpo",
    },
    "2021": {
        "Geral": "https://anuario2021.netlify.app/geral",
        "Graduação": "https://anuario2021.netlify.app/grad",
        "Pós-Graduação": "https://anuario2021.netlify.app/pos",
        "Mestrado": "https://anuario2021.netlify.app/mest",
        "Doutorado": "https://anuario2021.netlify.app/dout",
        "Produção Intelectual e Pesquisa": "https://anuario2021.netlify.app/pip",
        "Extensão": "https://anuario2021.netlify.app/ext",
        "Recursos Humanos": "https://anuario2021.netlify.app/rh",
        "Atividades Comunitárias": "https://anuario2021.netlify.app/comu",
        "Órgãos Complementares, Centros, Assessorias, Secretarias e Unidades Auxiliares": "https://anuario2021.netlify.app/org",
        "Planejamento, Execução Orçamentária e Convênios": "https://anuario2021.netlify.app/dpo",
    },
    "2022": {
        "Geral": "https://anuario2022.netlify.app/geral",
        "Graduação": "https://anuario2022.netlify.app/grad",
        "Pós-Graduação": "https://anuario2022.netlify.app/pos",
        "Mestrado": "https://anuario2022.netlify.app/mest",
        "Doutorado": "https://anuario2022.netlify.app/dout",
        "Produção Intelectual e Pesquisa": "https://anuario2022.netlify.app/pip",
        "Extensão": "https://anuario2022.netlify.app/ext",
        "Recursos Humanos": "https://anuario2022.netlify.app/rh",
        "Atividades Comunitárias": "https://anuario2022.netlify.app/comu",
        "Órgãos Complementares, Centros, Assessorias, Secretarias e Unidades Auxiliares": "https://anuario2022.netlify.app/org",
        "Planejamento, Execução Orçamentária e Convênios": "https://anuario2022.netlify.app/dpo",
    },
    "2023": {
        "Geral": "https://anuario2023.netlify.app/geral",
        "Graduação": "https://anuario2023.netlify.app/grad",
        "Pós-Graduação": "https://anuario2023.netlify.app/pos",
        "Mestrado": "https://anuario2023.netlify.app/mest",
        "Doutorado": "https://anuario2023.netlify.app/dout",
        "Produção Intelectual e Pesquisa": "https://anuario2023.netlify.app/pip",
        "Extensão": "https://anuario2023.netlify.app/ext",
        "Recursos Humanos": "https://anuario2023.netlify.app/rh",
        "Atividades Comunitárias": "https://anuario2023.netlify.app/comu",
        "Órgãos Complementares, Centros, Assessorias, Secretarias e Unidades Auxiliares": "https://anuario2023.netlify.app/org",
        "Planejamento, Execução Orçamentária e Convênios": "https://anuario2023.netlify.app/dpo",
    },
}

# Função para carregar conteúdo HTML de uma URL
def load_html_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    except Exception as e:
        st.error(f"Erro ao carregar a URL {url}: {e}")
        return None

# Função para limpar números do início dos títulos
def clean_title(title):
    return re.sub(r"^\d+\.\s*", "", title)

# Função para extrair tabelas com títulos
def extract_tables_and_titles(soup):
    tables = []
    titles = []
    for table in soup.find_all("table"):
        title_tag = table.find_previous("h3") or table.find_previous("h2")
        if title_tag:
            title_text = clean_title(title_tag.get_text(strip=True))
            titles.append(title_text)
        else:
            titles.append("Título desconhecido")
        tables.append(str(table))  # Manter formatação original da tabela
    return tables, titles

# Função para extrair gráficos com títulos
def extract_images_with_titles(soup, base_url):
    images = []
    titles = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            absolute_src = urljoin(base_url, src)
            title_tag = img.find_previous("h3") or img.find_previous("h2")
            title = clean_title(title_tag.get_text(strip=True)) if title_tag else "Gráfico sem título"
            titles.append(title)
            images.append(absolute_src)
    return images, titles

# Função para pesquisar em tabelas
def search_in_tables(tables, titles, search_term):
    results = []
    for table_html, title in zip(tables, titles):
        soup = BeautifulSoup(table_html, "html.parser")
        headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        rows = soup.find_all("tr")
        matching_rows = []
        for row in rows:
            row_text = [td.get_text(strip=True) for td in row.find_all("td")]
            if search_term.lower() in " ".join(row_text).lower():
                if headers:
                    row_with_headers = dict(zip(headers, row_text))
                else:
                    row_with_headers = {"Valores": row_text}
                matching_rows.append(row_with_headers)
        if matching_rows:
            results.append({"title": title, "matches": matching_rows})
    return results

# Configuração do Streamlit
st.set_page_config(page_title="Anuário Estatístico - UnB", layout="wide")
st.title("📊 Anuário Estatístico - UnB")

# Filtros
selected_year = st.sidebar.selectbox("📅 Selecione o Ano", list(URLS_BY_YEAR.keys()))
st.markdown(f"### Ano Selecionado: **{selected_year}**")

selected_section = st.sidebar.selectbox("📂 Selecione o Capítulo", list(URLS_BY_YEAR[selected_year].keys()))
content_type = st.sidebar.radio("🎯 Tipo de Conteúdo", ["Tabelas", "Gráficos"])
search_term = st.sidebar.text_input("🔍 Pesquisar por Nome do Curso ou Unidade (opcional):")

# Carregar dados da seção selecionada
soup = load_html_from_url(URLS_BY_YEAR[selected_year][selected_section])

if soup:
    if content_type == "Tabelas":
        tables, titles = extract_tables_and_titles(soup)
        if search_term:
            search_results = search_in_tables(tables, titles, search_term)
            if search_results:
                for result in search_results:
                    st.write(f"### {result['title']}")
                    for match in result["matches"]:
                        if isinstance(match, dict):
                            df = pd.DataFrame([match])
                            st.table(df)
                        else:
                            st.write(match)
            else:
                st.write("Nenhum resultado encontrado para a pesquisa.")
        else:
            if tables:
                for title, table_html in zip(titles, tables):
                    st.write(f"### {title}")
                    st.components.v1.html(table_html, height=400, scrolling=True)
            else:
                st.write("Nenhuma tabela encontrada.")
    elif content_type == "Gráficos":
        images, titles = extract_images_with_titles(soup, URLS_BY_YEAR[selected_year][selected_section])
        if images:
            for img, title in zip(images, titles):
                st.image(img, caption=title, use_container_width=True)
        else:
            st.write("Nenhum gráfico encontrado.")

# Rodapé
st.markdown("---")
st.markdown(
    "Desenvolvido para a **Universidade de Brasília (UnB)**. "
    "Se encontrar algum erro ou problema, por favor, entre em contato com a equipe técnica. DPO/DAI/CEI"
)
