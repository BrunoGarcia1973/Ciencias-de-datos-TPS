import pandas as pd
import os
import unicodedata
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
COLUMNAS_A_CONSERVAR = [
    "prod_pet", "prod_gas", "prod_agua", "tef",
    "tipoextraccion", "profundidad", "cuenca",
    "tipo_de_recurso", "tipopozo"
]

COLUMNAS_NUMERICAS = [
    "prod_pet", "prod_gas", "prod_agua",
    "tef", "profundidad"
]

COLUMNAS_CATEGORICAS = [
    "cuenca", "tipo_de_recurso", "tipoextraccion", "tipopozo"
]

# ------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------
def normalizar_texto(texto):
    if pd.isna(texto):
        return texto
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', errors='ignore').decode('utf-8')
    return texto

# ------------------------------------------------------------
# CARGA ROBUSTA
# ------------------------------------------------------------
def cargar_dataset(ruta=None):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    if ruta is None:
        posibles = [
            "produccion-de-pozos-de-gas-y-petroleo-unificado.csv.gz",
            "produccion-de-pozos-de-gas-y-petroleo-unificado.csv"
        ]

        for nombre in posibles:
            ruta_test = os.path.join(BASE_DIR, nombre)
            if os.path.exists(ruta_test):
                ruta = ruta_test
                break

    print(f"\n📥 Cargando dataset desde: {ruta}")

    if not ruta or not os.path.exists(ruta):
        raise FileNotFoundError(f"❌ No se encontró el archivo en: {ruta}")

    try:
        df = pd.read_csv(ruta, dtype=str, encoding='utf-8-sig', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, dtype=str, encoding='latin1', low_memory=False)

    return df

# ------------------------------------------------------------
# GRÁFICOS
# ------------------------------------------------------------
def graficar_nulos(df, titulo=""):
    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df)) * 100

    resumen = porcentaje[porcentaje > 0].sort_values(ascending=False)

    if resumen.empty:
        print(f"⚠️ No hay nulos ({titulo})")
        return

    plt.figure()
    resumen.plot(kind='bar')

    plt.title(f"Nulos (%) - {titulo}")
    plt.ylabel("Porcentaje")
    plt.xticks(rotation=45)
    plt.tight_layout()


def graficar_ceros(df, titulo=""):
    # 🔥 convertir todo lo posible a número
    df_num = df.copy()

    # manejar comas
    df_num = df_num.replace(",", ".", regex=True)

    # convertir
    df_num = df_num.apply(pd.to_numeric, errors='coerce')

    ceros = (df_num == 0).sum()
    porcentaje = (ceros / len(df_num)) * 100

    resumen = porcentaje[porcentaje > 0].sort_values(ascending=False)

    print("\n📊 DEBUG CEROS:")
    print(ceros[ceros > 0])

    if resumen.empty:
        print(f"⚠️ No hay ceros ({titulo})")
        return

    plt.figure()
    resumen.plot(kind='bar')

    plt.title(f"Ceros (%) - {titulo}")
    plt.ylabel("Porcentaje")
    plt.xticks(rotation=45)
    plt.tight_layout()

# ------------------------------------------------------------
# LIMPIEZAS
# ------------------------------------------------------------
def eliminar_duplicados(df):
    if 'fechaingreso' in df.columns:
        df['fechaingreso'] = pd.to_datetime(df['fechaingreso'], errors='coerce')
        df = df.sort_values(by='fechaingreso', ascending=False)

    columnas_pk = ['idpozo', 'anio', 'mes']
    columnas_subset = [col for col in columnas_pk if col in df.columns]

    if len(columnas_subset) == 3:
        df = df.drop_duplicates(subset=columnas_subset, keep='first').copy()
    else:
        df = df.drop_duplicates().copy()

    return df

def seleccionar_columnas(df):
    cols = [c for c in COLUMNAS_A_CONSERVAR if c in df.columns]
    return df[cols].copy()

def convertir_coma_a_punto(df):
    for col in COLUMNAS_NUMERICAS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def filtrar_habilitados(df):
    if 'habilitado' in df.columns:
        df = df[df['habilitado'].str.lower() == 't'].copy()
    return df

def limpiar_categoricas(df):
    for col in COLUMNAS_CATEGORICAS:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_texto)
    return df

def eliminar_outliers_iqr(df, col):
    if col in df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        df = df[(df[col] >= Q1 - 1.5 * IQR) &
                (df[col] <= Q3 + 1.5 * IQR)]
    return df

def filtrar_prod_pet_valido(df):
    if 'prod_pet' in df.columns:
        df = df[df['prod_pet'] > 0]
    return df

def filtrar_tipopozo_petrolifero(df):
    if 'tipopozo' in df.columns:
        df = df[df['tipopozo'] == 'petrolifero']
    return df

# ------------------------------------------------------------
# IMPUTACIÓN
# ------------------------------------------------------------
def imputar_profundidad(df):
    df['profundidad'] = df['profundidad'].fillna(
        df.groupby(['cuenca', 'tipo_de_recurso'])['profundidad'].transform('median')
    )
    return df

def imputar_tef(df):
    df['tef'] = df['tef'].fillna(
        df.groupby('tipoextraccion')['tef'].transform('median')
    )
    return df

# ------------------------------------------------------------
# PIPELINE
# ------------------------------------------------------------
def limpiar_dataset(df):
    print("\n🧹 Iniciando limpieza...")

    # 🔥 ANTES
    graficar_nulos(df, "ANTES")
    graficar_ceros(df, "ANTES")

    df = filtrar_habilitados(df)
    df = convertir_coma_a_punto(df)
    df = eliminar_duplicados(df)

    # 🔥 pierde columnas
    df = seleccionar_columnas(df)

    graficar_nulos(df, "POST-SELECCIÓN")
    graficar_ceros(df, "POST-SELECCIÓN")

    df = limpiar_categoricas(df)
    df = filtrar_prod_pet_valido(df)
    df = filtrar_tipopozo_petrolifero(df)
    df = imputar_profundidad(df)
    df = imputar_tef(df)

    for col in ["prod_pet", "prod_gas"]:
        df = eliminar_outliers_iqr(df, col)

    # 🔥 FINAL
    graficar_nulos(df, "FINAL")
    graficar_ceros(df, "FINAL")

    print(f"📊 Shape final: {df.shape}")
    return df

# ------------------------------------------------------------
# GUARDADO
# ------------------------------------------------------------
def guardar_dataset(df):
    os.makedirs("csv_limpio", exist_ok=True)
    ruta = "csv_limpio/salida.csv"
    df.to_csv(ruta, index=False)
    print(f"✅ Guardado en: {ruta}")

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    df = cargar_dataset()

    df_limpio = limpiar_dataset(df)

    guardar_dataset(df_limpio)

    print("\nResumen:")
    print("Original:", len(df))
    print("Limpio:", len(df_limpio))

    plt.show()

# ------------------------------------------------------------
if __name__ == "__main__":
    main()