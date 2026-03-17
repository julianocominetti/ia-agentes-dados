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


def ordenar(df, coluna="2026"):
    if coluna in df.columns:
        return df.sort_values(coluna, ascending=False)
    return df


def linha(row):
    return " | ".join([f"{col}:{row[col]}" for col in row.index])


# ===============================
# LEITURA
# ===============================

print("📥 Lendo arquivos...")

cliente = ler("CLIENTE")
filial = ler("FILIAL")
vendedor = ler("VENDEDOR")
grupo = ler("GRUPO")


# ===============================
# TRATAMENTO
# ===============================

for df in [cliente, filial, vendedor, grupo]:
    for col in ["2025", "2026", "CODFILIAL"]:
        df = garantir_coluna(df, col)

for df in [cliente, filial, vendedor, grupo]:
    for col in ["2025", "2026"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# ===============================
# GERAR TEXTO
# ===============================

print("🧠 Gerando base...")

texto = ""
texto += "BASE COMERCIAL CANTU\n"
texto += "ANALISE COMERCIAL INTELIGENTE\n\n"


# FILIAIS
texto += "============================\nINSIGHT FILIAIS\n============================\n\n"
for i, (_, f) in enumerate(ordenar(filial).iterrows(), start=1):
    texto += f"RANKING:{i} | {linha(f)}\n"


# CLIENTES
texto += "\n============================\nTOP CLIENTES\n============================\n\n"
for i, (_, c) in enumerate(ordenar(cliente).head(20).iterrows(), start=1):
    texto += f"RANKING:{i} | {linha(c)}\n"


# VENDEDORES
texto += "\n============================\nTOP VENDEDORES\n============================\n\n"
for i, (_, v) in enumerate(ordenar(vendedor).head(20).iterrows(), start=1):
    texto += f"RANKING:{i} | {linha(v)}\n"


# GRUPOS
texto += "\n============================\nTOP CATEGORIAS\n============================\n\n"
for i, (_, g) in enumerate(ordenar(grupo).head(20).iterrows(), start=1):
    texto += f"RANKING:{i} | {linha(g)}\n"


# ===============================
# SALVAR TXT
# ===============================

os.makedirs(PASTA_DADOS, exist_ok=True)

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(texto)

print(f"✅ Base gerada: {ARQUIVO_SAIDA}")


# ===============================
# GIT AUTOMÁTICO
# ===============================

def run_git(comando):
    return subprocess.run(comando, cwd="/Users/julianodesa/Downloads/ia-agentes-dados")


print("🚀 Atualizando GitHub...")

try:
    run_git(["git", "add", "."])

    # commit só se tiver alteração
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd="/Users/julianodesa/Downloads/ia-agentes-dados"
    )

    if status.stdout.strip() == "":
        print("ℹ️ Nenhuma alteração para commit")
    else:
        mensagem = f"Atualizacao automatica Cantu {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        run_git(["git", "commit", "-m", mensagem])
        run_git(["git", "push"])
        print("✅ GitHub atualizado com sucesso!")

except Exception as e:
    print("❌ Erro ao atualizar Git:", e)


print("🏁 PROCESSO FINALIZADO")