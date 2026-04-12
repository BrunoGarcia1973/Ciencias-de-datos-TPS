import pandas as pd
import os
from probando_CD1 import cargar_dataset, auditar_categoricas  # Asegurate de que el nombre del módulo coincida

# ------------------------------------------------------------
# Funciones de limpieza
# ------------------------------------------------------------

def convertir_coma_a_punto(df):
    """
    Reemplaza la coma decimal por punto en las columnas numéricas que estén como texto.
    Luego convierte las columnas a tipo float.
    """
    columnas_numericas = [
        'prod_pet', 'prod_gas', 'prod_agua', 'iny_agua',
        'iny_gas', 'iny_co2', 'iny_otro', 'tef', 'profundidad'
    ]
    for col in columnas_numericas:
        if col in df.columns:
            # Si la columna es de tipo object, puede tener comas
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            # Convertir a numérico, forzando errores a NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def filtrar_prod_pet_no_cero(df):
    """
    Elimina las filas donde la producción de petróleo (prod_pet) sea 0 o 0.0.
    """
    if 'prod_pet' in df.columns:
        # Asegurar que sea numérico
        df['prod_pet'] = pd.to_numeric(df['prod_pet'], errors='coerce')
        df = df[df['prod_pet'] != 0]
        df = df.dropna(subset=['prod_pet'])  # también elimina NaN
    return df

def limpiar_dataset(df):
    """
    Aplica todas las transformaciones de limpieza en orden.
    """
    df = convertir_coma_a_punto(df)
    df = filtrar_prod_pet_no_cero(df)
    return df

# ------------------------------------------------------------
# Función para guardar dataset limpio
# ------------------------------------------------------------

def guardar_dataset_limpio(df, ruta_original, carpeta_salida="csv limpio"):
    """
    Guarda el DataFrame limpio en una subcarpeta con el prefijo 'LIMPIO-'.
    """
    # Crear carpeta si no existe
    os.makedirs(carpeta_salida, exist_ok=True)

    # Obtener nombre base del archivo original
    nombre_base = os.path.basename(ruta_original)
    nombre_limpio = f"LIMPIO-{nombre_base}"
    ruta_guardado = os.path.join(carpeta_salida, nombre_limpio)

    df.to_csv(ruta_guardado, index=False, encoding='utf-8')
    print(f"✅ Dataset limpio guardado en: {ruta_guardado}")
    return ruta_guardado

# ------------------------------------------------------------
# Main del proceso ETL
# ------------------------------------------------------------

def main():
    # 1. Cargar dataset original (usando la función del otro módulo)
    ruta_original = None  # Usa el valor por defecto definido en cargar_dataset()
    df_original = cargar_dataset(ruta_original)

    # 2. Aplicar limpieza
    print("\n🧹 Iniciando limpieza del dataset...")
    df_limpio = limpiar_dataset(df_original.copy())  # Copia para no modificar el original

    # 3. Guardar dataset limpio
    ruta_guardado = guardar_dataset_limpio(df_limpio, ruta_original or "produccion-de-pozos-de-gas-y-petroleo-no-convencional-_Autoguardado_.csv")

    # 4. Auditoría comparativa
    columnas_categoricas = ['cuenca', 'tipo_de_recurso', 'tipoextraccion']

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