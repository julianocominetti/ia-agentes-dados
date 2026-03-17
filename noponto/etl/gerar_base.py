import pandas as pd
from datetime import datetime
import glob
import os
import subprocess

# ==========================================
# CAMINHOS
# ==========================================

ETL_DIR = os.path.dirname(os.path.abspath(__file__))
NOPONTO_DIR = os.path.dirname(ETL_DIR)
REPO_DIR = os.path.dirname(NOPONTO_DIR)

PASTA_EXCEL = os.path.join(NOPONTO_DIR, "excel")
PASTA_DADOS = os.path.join(NOPONTO_DIR, "dados")

ARQUIVO_SAIDA = os.path.join(PASTA_DADOS, "base_noponto.txt")

# ==========================================
# EXECUTOR DE COMANDOS
# ==========================================

def run(cmd):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)

# ==========================================
# LEITOR UNIVERSAL
# ==========================================

def ler_arquivo(nome):

    arquivos = glob.glob(os.path.join(PASTA_EXCEL, f"{nome}.*"))

    if not arquivos:
        raise Exception(f"Arquivo {nome} não encontrado")

    caminho = arquivos[0]
    ext = os.path.splitext(caminho)[1].lower()

    if ext == ".xlsx":
        df = pd.read_excel(caminho, engine="openpyxl")

    elif ext == ".xls":
        df = pd.read_excel(caminho, engine="xlrd")

    elif ext == ".csv":
        df = pd.read_csv(caminho, sep=";", encoding="latin1")

    else:
        raise Exception("Formato não suportado")

    df.columns = [c.strip().upper() for c in df.columns]

    return df

# ==========================================
# LEITURA DOS DADOS
# ==========================================

print("Lendo arquivos...")

lojas = ler_arquivo("lojas_26")
produtos = ler_arquivo("produtos_26")
lojas_marco = ler_arquivo("lojas_26marco")
produtos_marco = ler_arquivo("produtos_26marco")

# ==========================================
# CONVERSÃO NUMÉRICA
# ==========================================

def converter(df, colunas):
    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

converter(lojas, ["RANKING","FATURAMENTOLOJA","REPRESENTALOJA"])
converter(lojas_marco, ["RANKING","FATURAMENTOLOJA","REPRESENTALOJA"])

converter(produtos, ["RANKING","FATURAMENTOPRODUTO","REPRESENTAPRODUTO"])
converter(produtos_marco, ["RANKING","FATURAMENTOPRODUTO","REPRESENTAPRODUTO"])

# ==========================================
# ORDENAÇÃO
# ==========================================

lojas = lojas.sort_values("RANKING")
lojas_marco = lojas_marco.sort_values("RANKING")

produtos = produtos.sort_values("RANKING")
produtos_marco = produtos_marco.sort_values("RANKING")

# ==========================================
# CÁLCULOS
# ==========================================

faturamento = lojas["FATURAMENTOLOJA"].sum()
faturamento_marco = lojas_marco["FATURAMENTOLOJA"].sum()

hoje = datetime.today()
dia_ano = hoje.timetuple().tm_yday

media = faturamento / max(dia_ano, 1)
projecao = media * 365

# ==========================================
# CASHBACK
# ==========================================

if projecao >= 35000000:
    faixa = "1.50"
elif projecao >= 30000000:
    faixa = "1.25"
elif projecao >= 26500000:
    faixa = "1.00"
else:
    faixa = "0"

# ==========================================
# GERAR BASE TXT
# ==========================================

print("Gerando base...")

texto = ""

texto += "BASE_REDE\n"
texto += f"DATA={hoje.strftime('%Y-%m-%d')}\n"
texto += f"FATURAMENTO_2026={faturamento:.2f}\n"
texto += f"MEDIA_DIARIA={media:.2f}\n"
texto += f"PROJECAO_ANUAL={projecao:.2f}\n"
texto += f"FATURAMENTO_MARCO={faturamento_marco:.2f}\n"
texto += f"CASHBACK_FAIXA={faixa}\n\n"

# LOJAS
texto += "LOJAS\n"
for _, r in lojas.iterrows():
    texto += f"{int(r['RANKING'])}|{r['NOMELOJA']}|{r['REPRESENTALOJA']:.4f}|{r['FATURAMENTOLOJA']:.2f}\n"

# LOJAS MARÇO
texto += "\nLOJAS_MARCO\n"
for _, r in lojas_marco.iterrows():
    texto += f"{int(r['RANKING'])}|{r['NOMELOJA']}|{r['REPRESENTALOJA']:.4f}|{r['FATURAMENTOLOJA']:.2f}\n"

# PRODUTOS
texto += "\nPRODUTOS\n"
for _, r in produtos.head(50).iterrows():
    texto += f"{int(r['RANKING'])}|{r['NOMEPRODUTO']}|{r['REPRESENTAPRODUTO']:.4f}|{r['FATURAMENTOPRODUTO']:.2f}\n"

# PRODUTOS MARÇO
texto += "\nPRODUTOS_MARCO\n"
for _, r in produtos_marco.head(50).iterrows():
    texto += f"{int(r['RANKING'])}|{r['NOMEPRODUTO']}|{r['REPRESENTAPRODUTO']:.4f}|{r['FATURAMENTOPRODUTO']:.2f}\n"

# ==========================================
# SALVAR BASE
# ==========================================

os.makedirs(PASTA_DADOS, exist_ok=True)

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(texto)

print("Base gerada:", ARQUIVO_SAIDA)

# ==========================================
# GIT AUTOMÁTICO (VERSÃO FINAL)
# ==========================================

print("Atualizando GitHub...")

os.chdir(REPO_DIR)

# adiciona arquivo
run(["git", "add", "noponto/dados/base_noponto.txt"])

# verifica se houve alteração real
diff = subprocess.run(["git", "diff", "--cached", "--quiet"])

if diff.returncode == 0:
    print("Nenhuma alteração real na base. Nada para enviar.")

else:
    print("Alterações detectadas...")

    run(["git", "commit", "-m", "Atualizacao automatica base noponto"])
    run(["git", "push"])

    print("GitHub atualizado com sucesso!")