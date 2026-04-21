import pandas as pd

# RUTAS COMPLETAS
base_path = r"C:\Users\Maxi\Desktop\joji\unificador csv petroleo"

archivo_con_coordenadas = base_path + r"\produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"
archivo_sin_coordenadas = base_path + r"\produccin-de-pozos-de-gas-y-petrleo-2026.csv"

# 🔥 ahora guardamos comprimido
archivo_salida = base_path + r"\produccin-de-pozos-de-gas-y-petrleo-unificado.csv.gz"

# Leer CSVs
df1 = pd.read_csv(archivo_con_coordenadas, encoding="utf-8-sig")
df2 = pd.read_csv(archivo_sin_coordenadas, encoding="utf-8-sig")

# Agregar columnas faltantes
for columna in ["coordenadax", "coordenaday"]:
    if columna not in df2.columns:
        df2[columna] = None

# Igualar columnas
df2 = df2[df1.columns]

# Unir
df_unificado = pd.concat([df1, df2], ignore_index=True)

# 🔽 OPTIMIZACIONES

# 1. Redondear floats (menos peso)
df_unificado = df_unificado.round(4)

# 2. Limpiar espacios en strings
for col in df_unificado.select_dtypes(include="object").columns:
    df_unificado[col] = df_unificado[col].str.strip()

# 3. Guardar comprimido
df_unificado.to_csv(
    archivo_salida,
    index=False,
    encoding="utf-8-sig",
    compression="gzip"
)

print("Archivo unificado y comprimido creado correctamente")