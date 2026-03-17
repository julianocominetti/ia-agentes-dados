import pandas as pd
import glob
import os

# ===============================
# CAMINHO DA BASE
# ===============================

pasta = "/Users/julianodesa/Downloads/IA CANTU"


# ===============================
# LEITOR UNIVERSAL (XLS XLSX CSV)
# ===============================

def ler(nome):

    arquivos = glob.glob(f"{pasta}/{nome}.*")

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

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n","")
        .str.replace("\r","")
        .str.upper()
    )

    return df


# ===============================
# LER ARQUIVOS
# ===============================

cliente = ler("CLIENTE")
filial = ler("FILIAL")
vendedor = ler("VENDEDOR")
grupo = ler("GRUPO")


# ===============================
# CONVERTER NUMERICO
# ===============================

for df in [cliente, filial, vendedor, grupo]:

    for col in ["2025","2026"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


# ===============================
# FUNÇÃO PARA MOSTRAR TODAS COLUNAS
# ===============================

def linha(row):

    texto = ""

    for col in row.index:
        texto += f"{col}:{row[col]} | "

    return texto[:-3]


# ===============================
# INICIO DO TEXTO
# ===============================

texto = ""

texto += "BASE COMERCIAL CANTU\n"
texto += "ANALISE COMERCIAL INTELIGENTE\n\n"


# ===============================
# INSIGHTS - TODAS AS FILIAIS
# ===============================

texto += "============================\n"
texto += "INSIGHT EXECUTIVO - FILIAIS\n"
texto += "============================\n\n"

filiais_rank = filial.sort_values("2026", ascending=False)

ranking = 1

for _, f in filiais_rank.iterrows():

    texto += f"RANKING:{ranking} | "

    texto += linha(f) + "\n"

    ranking += 1


# ===============================
# TOP CLIENTES EMPRESA
# ===============================

texto += "\n============================\n"
texto += "TOP 20 CLIENTES EMPRESA\n"
texto += "============================\n\n"

top_clientes = cliente.sort_values("2026", ascending=False).head(20)

ranking = 1

for _, c in top_clientes.iterrows():

    texto += f"RANKING:{ranking} | "

    texto += linha(c) + "\n"

    ranking += 1


# ===============================
# TOP VENDEDORES EMPRESA
# ===============================

texto += "\n============================\n"
texto += "TOP 20 VENDEDORES EMPRESA\n"
texto += "============================\n\n"

top_vendedores = vendedor.sort_values("2026", ascending=False).head(20)

ranking = 1

for _, v in top_vendedores.iterrows():

    texto += f"RANKING:{ranking} | "

    texto += linha(v) + "\n"

    ranking += 1


# ===============================
# TOP CATEGORIAS EMPRESA
# ===============================

texto += "\n============================\n"
texto += "TOP 20 CATEGORIAS EMPRESA\n"
texto += "============================\n\n"

top_grupos = grupo.sort_values("2026", ascending=False).head(20)

ranking = 1

for _, g in top_grupos.iterrows():

    texto += f"RANKING:{ranking} | "

    texto += linha(g) + "\n"

    ranking += 1


# ===============================
# ANALISE POR FILIAL
# ===============================

texto += "\n============================\n"
texto += "ANALISE DETALHADA POR FILIAL\n"
texto += "============================\n\n"

for _, f in filial.iterrows():

    cod = f["CODFILIAL"]

    texto += "\n----------------------------------\n"
    texto += "FILIAL\n"
    texto += linha(f) + "\n"


    # CLIENTES FILIAL

    texto += "\nTOP 20 CLIENTES FILIAL\n"

    clientes_filial = cliente[cliente["CODFILIAL"] == cod]

    clientes_filial = clientes_filial.sort_values("2026", ascending=False).head(20)

    for _, c in clientes_filial.iterrows():

        texto += linha(c) + "\n"


    # VENDEDORES FILIAL

    texto += "\nVENDEDORES FILIAL\n"

    vendedores_filial = vendedor[vendedor["CODFILIAL"] == cod]

    vendedores_filial = vendedores_filial.sort_values("2026", ascending=False)

    for _, v in vendedores_filial.iterrows():

        texto += linha(v) + "\n"


    # GRUPOS FILIAL

    texto += "\nGRUPOS FILIAL\n"

    grupos_filial = grupo[grupo["CODFILIAL"] == cod]

    grupos_filial = grupos_filial.sort_values("2026", ascending=False)

    for _, g in grupos_filial.iterrows():

        texto += linha(g) + "\n"


# ===============================
# BASE COMPLETA
# ===============================

texto += "\n============================\n"
texto += "BASE COMPLETA\n"
texto += "============================\n\n"


texto += "\nCLIENTES\n"

for _, c in cliente.iterrows():

    texto += linha(c) + "\n"


texto += "\nVENDEDORES\n"

for _, v in vendedor.iterrows():

    texto += linha(v) + "\n"


texto += "\nGRUPOS\n"

for _, g in grupo.iterrows():

    texto += linha(g) + "\n"


texto += "\nFILIAIS\n"

for _, f in filial.iterrows():

    texto += linha(f) + "\n"


# ===============================
# SALVAR
# ===============================

saida = f"{pasta}/BASE_ANALISE_CANTU_COMPLETA.txt"

with open(saida, "w", encoding="utf-8") as f:

    f.write(texto)


print("BASE COMPLETA GERADA COM SUCESSO")
print("Arquivo criado:", saida)