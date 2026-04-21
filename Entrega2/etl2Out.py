import pandas as pd
import os
import unicodedata
from probando_CD1 import cargar_dataset, auditar_categoricas

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
# Funciones base
# ------------------------------------------------------------
def normalizar_texto(texto):
    if pd.isna(texto):
        return texto
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', errors='ignore').decode('utf-8')
    return texto


def seleccionar_columnas(df):
    columnas_existentes = [col for col in COLUMNAS_A_CONSERVAR if col in df.columns]
    faltantes = set(COLUMNAS_A_CONSERVAR) - set(columnas_existentes)
    if faltantes:
        print(f"⚠️ Columnas no encontradas: {faltantes}")
    return df[columnas_existentes].copy()


def convertir_coma_a_punto(df):
    for col in COLUMNAS_NUMERICAS:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# ------------------------------------------------------------
# Limpiezas
# ------------------------------------------------------------
def limpiar_categoricas(df):
    for col in COLUMNAS_CATEGORICAS:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_texto)
    return df


def eliminar_duplicados(df):
    antes = len(df)
    df = df.drop_duplicates(subset=COLUMNAS_A_CONSERVAR).copy()
    despues = len(df)
    print(f"🧹 Duplicados eliminados: {antes - despues}")
    return df


def eliminar_outliers_iqr(df, columna):
    if columna in df.columns:
        Q1 = df[columna].quantile(0.25)
        Q3 = df[columna].quantile(0.75)
        IQR = Q3 - Q1

        limite_inf = Q1 - 1.5 * IQR
        limite_sup = Q3 + 1.5 * IQR

        antes = len(df)

        df = df[
            (df[columna] >= limite_inf) &
            (df[columna] <= limite_sup)
        ].copy()

        despues = len(df)

        print(f"📉 Outliers eliminados en {columna}: {antes - despues}")

    return df

# ------------------------------------------------------------
# Filtros específicos
# ------------------------------------------------------------
def filtrar_prod_pet_valido(df):
    if 'prod_pet' in df.columns:
        df['prod_pet'] = pd.to_numeric(df['prod_pet'], errors='coerce')
        df = df[df['prod_pet'] > 0].copy()
    return df


def filtrar_tipopozo_petrolifero(df):
    if 'tipopozo' in df.columns:
        df = df[df['tipopozo'] == 'petrolifero'].copy()
    else:
        print("⚠️ Columna 'tipopozo' no encontrada.")
    return df

# ------------------------------------------------------------
# PIPELINE
# ------------------------------------------------------------
def limpiar_dataset(df):
    df = df.copy()

    print("\n🧹 Iniciando limpieza del dataset...")

    # 1. Conversión de tipos
    df = convertir_coma_a_punto(df)

    # 2. Selección de columnas
    df = seleccionar_columnas(df)

    # 3. Limpiezas generales
    df = limpiar_categoricas(df)
    df = eliminar_duplicados(df)

    # 4. Filtros
    df = filtrar_prod_pet_valido(df)
    df = filtrar_tipopozo_petrolifero(df)

    # 5. Outliers (en múltiples columnas)
    for col in ["prod_pet", "prod_gas"]:
        df = eliminar_outliers_iqr(df, col)

    print(f"\n📊 Shape final: {df.shape}")

    return df

# ------------------------------------------------------------
# Guardado
# ------------------------------------------------------------
def guardar_dataset_limpio(df, ruta_original, carpeta_salida="csv_limpio"):
    os.makedirs(carpeta_salida, exist_ok=True)

    nombre_base = os.path.basename(ruta_original)
    nombre_limpio = f"LIMPIO-{nombre_base}"
    ruta_guardado = os.path.join(carpeta_salida, nombre_limpio)

    df.to_csv(ruta_guardado, index=False, encoding='utf-8')

    print(f"✅ Dataset limpio guardado en: {ruta_guardado}")
    return ruta_guardado

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    ruta_original = None
    df_original = cargar_dataset(ruta_original)

    df_limpio = limpiar_dataset(df_original)

    guardar_dataset_limpio(
        df_limpio,
        ruta_original or "produccion-de-pozos-de-gas-y-petroleo-unificado.csv.gz"
    )

    columnas_categoricas = ['cuenca', 'tipo_de_recurso', 'tipoextraccion', 'tipopozo']

    print("\n🔍 AUDITORÍA ORIGINAL")
    auditar_categoricas(df_original, columnas_categoricas)

    print("\n🔍 AUDITORÍA LIMPIO")
    auditar_categoricas(df_limpio, columnas_categoricas)

    print("\n📈 Resumen:")
    print(f"Filas originales: {len(df_original)}")
    print(f"Filas limpias: {len(df_limpio)}")

    print("\n📊 Tipos de datos:")
    print(df_limpio.dtypes)


if __name__ == "__main__":
    main()