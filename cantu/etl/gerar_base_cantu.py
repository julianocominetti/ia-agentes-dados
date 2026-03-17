import pandas as pd
import glob
import os
import subprocess
from datetime import datetime

# ===============================
# CAMINHOS
# ===============================

BASE_DIR = "/Users/julianodesa/Downloads/ia-agentes-dados/cantu"
PASTA_EXCEL = f"{BASE_DIR}/excel"
PASTA_DADOS = f"{BASE_DIR}/dados"

ARQUIVO_SAIDA = f"{PASTA_DADOS}/base_cantu.txt"


# ===============================
# LEITOR UNIVERSAL
# ===============================

def ler(nome):

    arquivos = glob.glob(f"{PASTA_EXCEL}/{nome}.*")

    if not arquivos:
        raise Exception(f"Arquivo {nome} não encontrado em {PASTA_EXCEL}")

    caminho = arquivos[0]
    ext = os.path.splitext(caminho)[1].lower()

    if ext == ".xlsx":
        df = pd.read_excel(caminho, engine="openpyxl")

    elif ext == ".xls":
        df = pd.read_excel(caminho, engine="xlrd")

    elif ext == ".csv":
        df = pd.read_csv(caminho, sep=";", encoding="latin1")

    else:
        raise Exception(f"Formato não suportado: {ext}")

    # padroniza colunas
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "")
        .str.replace("\r", "")
        .str.upper()
    )

    return df


# ===============================
# FUNÇÕES AUXILIARES
# ===============================

def garantir_coluna(df, coluna):
    if coluna not in df.columns:
        df[coluna] = 0
    return df


def preparar_df(df):
    for col in ["2025", "2026", "META", "MARGEM", "CODFILIAL"]:
        df = garantir_coluna(df, col)

    for col in ["2025", "2026", "META", "MARGEM"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def gerar_linha(row, tipo):

    partes = [f"TIPO:{tipo}"]

    for col in row.index:

        valor = row[col]

        # evita quebrar formato
        if isinstance(valor, str):
            valor = valor.replace("|", " ").strip()

        partes.append(f"{col}:{valor}")

    return " | ".join(partes)


# ===============================
# LEITURA DOS ARQUIVOS
# ===============================

print("📥 Lendo arquivos...")

cliente = preparar_df(ler("CLIENTE"))
filial = preparar_df(ler("FILIAL"))
vendedor = preparar_df(ler("VENDEDOR"))
grupo = preparar_df(ler("GRUPO"))


# ===============================
# GERAÇÃO DO TEXTO
# ===============================

print("🧠 Gerando base estruturada...")

linhas = []

linhas.append("BASE COMERCIAL CANTU")
linhas.append(f"ATUALIZADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
linhas.append("")


# FILIAIS
for _, row in filial.iterrows():
    linhas.append(gerar_linha(row, "FILIAL"))

# CLIENTES
for _, row in cliente.iterrows():
    linhas.append(gerar_linha(row, "CLIENTE"))

# VENDEDORES
for _, row in vendedor.iterrows():
    linhas.append(gerar_linha(row, "VENDEDOR"))

# GRUPOS
for _, row in grupo.iterrows():
    linhas.append(gerar_linha(row, "GRUPO"))


# ===============================
# SALVAR TXT
# ===============================

os.makedirs(PASTA_DADOS, exist_ok=True)

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))

print(f"✅ Base gerada com sucesso: {ARQUIVO_SAIDA}")


# ===============================
# GIT AUTOMÁTICO
# ===============================

def run_git(cmd):
    return subprocess.run(cmd, cwd="/Users/julianodesa/Downloads/ia-agentes-dados")


print("🚀 Enviando para GitHub...")

try:
    run_git(["git", "add", "."])

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd="/Users/julianodesa/Downloads/ia-agentes-dados"
    )

    if status.stdout.strip() == "":
        print("ℹ️ Nenhuma alteração detectada")
    else:
        msg = f"Atualizacao automatica Cantu {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        run_git(["git", "commit", "-m", msg])
        run_git(["git", "push"])
        print("✅ GitHub atualizado!")

except Exception as e:
    print("❌ Erro no Git:", e)


print("🏁 PROCESSO FINALIZADO")