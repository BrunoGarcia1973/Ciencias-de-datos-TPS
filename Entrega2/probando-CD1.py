import pandas as pd
import os

# --- EL TRUCO PRO PARA VS CODE ---
# Esto le dice a Python: "Buscá la ruta exacta de ESTE script (.py) y usala como base"
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Nombre exacto de tu archivo (corregido: sin espacio antes del paréntesis)
nombre_archivo = 'produccin-de-pozos-de-gas-y-petrleo-no-convencional(Autoguardado).csv' 

# Armamos la ruta absoluta (C:\Users\...\PROBANDO CD\archivo.csv)
ruta_completa = os.path.join(directorio_actual, nombre_archivo)

print("Cargando dataset, por favor esperá...\n")

# Carga robusta usando la ruta completa
try:
    # Intentamos primero con utf-8
    df = pd.read_csv(ruta_completa, encoding='utf-8', sep=',')
except UnicodeDecodeError:
    # Si falla por las tildes, usamos latin1
    df = pd.read_csv(ruta_completa, encoding='latin1', sep=',')
except FileNotFoundError:
    print(f"❌ ERROR: Sigo sin encontrar el archivo.")
    print(f"Python lo está buscando exactamente acá:\n{ruta_completa}")
    raise SystemExit()

# Lista de columnas a auditar
columnas_a_auditar = ['cuenca', 'tipo_de_recurso', 'tipoextraccion']

print("=== 📊 AUDITORÍA DE VARIABLES CATEGÓRICAS ===\n")

for col in columnas_a_auditar:
    if col in df.columns:
        print(f"--- Frecuencia para: {col.upper()} ---")
        conteo = df[col].value_counts(dropna=False)
        print(conteo)
        
        unicos = df[col].nunique()
        print(f"📌 Total de categorías distintas: {unicos}")
        print("-" * 40 + "\n")
    else:
        print(f"⚠️ ATENCIÓN: La columna '{col}' no existe. Revisá si hay espacios extra en el nombre en tu Excel.\n")