import pandas as pd
import os
from probando_CD1 import cargar_dataset, auditar_categoricas

# ------------------------------------------------------------
# Configuración para el nuevo dataset
# ------------------------------------------------------------
COLUMNAS_A_CONSERVAR = [
    "prod_pet", "prod_gas", "prod_agua", "tef",
    "tipoextraccion", "profundidad", "cuenca",
    "tipo_de_recurso", "tipopozo"
]

# ------------------------------------------------------------
# Funciones de limpieza
# ------------------------------------------------------------
def seleccionar_columnas(df):
    """Mantiene únicamente las columnas necesarias."""
    columnas_existentes = [col for col in COLUMNAS_A_CONSERVAR if col in df.columns]
    faltantes = set(COLUMNAS_A_CONSERVAR) - set(columnas_existentes)
    if faltantes:
        print(f"⚠️ Columnas no encontradas: {faltantes}")
    return df[columnas_existentes]

def convertir_coma_a_punto(df):
    """Convierte coma decimal a punto en columnas numéricas."""
    columnas_numericas = [
        'prod_pet', 'prod_gas', 'prod_agua', 'iny_agua',
        'iny_gas', 'iny_co2', 'iny_otro', 'tef', 'profundidad'
    ]
    for col in columnas_numericas:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def filtrar_prod_pet_no_cero(df):
    """Elimina filas con prod_pet igual a 0 o NaN."""
    if 'prod_pet' in df.columns:
        df['prod_pet'] = pd.to_numeric(df['prod_pet'], errors='coerce')
        df = df[df['prod_pet'] != 0]
        df = df.dropna(subset=['prod_pet'])
    return df

def filtrar_tipopozo_petrolifero(df):
    """Conserva solo pozos Petrolíferos."""
    if 'tipopozo' in df.columns:
        df = df[df['tipopozo'] == 'Petrolífero']
    else:
        print("⚠️ Columna 'tipopozo' no encontrada, no se aplica filtro.")
    return df

def limpiar_dataset(df):
    """Pipeline completo de limpieza."""
    df = seleccionar_columnas(df)
    df = convertir_coma_a_punto(df)
    df = filtrar_prod_pet_no_cero(df)
    df = filtrar_tipopozo_petrolifero(df)
    return df


# ------------------------------------------------------------
# Guardado
# ------------------------------------------------------------
def guardar_dataset_limpio(df, ruta_original, carpeta_salida="csv limpio"):
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
    # 1. Cargar dataset original (usará el nuevo nombre por defecto)
    ruta_original = None  # usamos el default de probando_CD1
    df_original = cargar_dataset(ruta_original)

    # 2. Limpiar
    print("\n🧹 Iniciando limpieza del dataset...")
    df_limpio = limpiar_dataset(df_original.copy())

    # 3. Guardar
    ruta_guardado = guardar_dataset_limpio(
        df_limpio,
        ruta_original or "produccion-de-pozos-de-gas-y-petroleo-unificado.csv.gz"
    )

    # 4. Auditoría comparativa
    columnas_categoricas = ['cuenca', 'tipo_de_recurso', 'tipoextraccion', 'tipopozo']

    print("\n🔍 AUDITORÍA DEL DATASET ORIGINAL")
    auditar_categoricas(df_original, columnas_categoricas)

    print("\n🔍 AUDITORÍA DEL DATASET LIMPIO")
    auditar_categoricas(df_limpio, columnas_categoricas)

    print("\n📈 Resumen de cambio de tamaño:")
    print(f" - Filas originales: {len(df_original)}")
    print(f" - Filas después de limpieza: {len(df_limpio)}")
    print(f" - Filas eliminadas: {len(df_original) - len(df_limpio)}")

if __name__ == "__main__":
    main()
