
import os
import pandas as pd
import matplotlib.pyplot as plt

from probando_CD1 import cargar_dataset

# =========================
# CARGA DE DATOS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ruta = os.path.join(BASE_DIR, "..", "..", "csv_limpio", "salida.csv")

df = pd.read_csv(ruta)

print("Shape del dataset:", df.shape)

# =========================
# DETECCIÓN DE CEROS
# =========================

# Solo columnas numéricas (IMPORTANTE)
df_numericas = df.select_dtypes(include=['number'])

ceros = (df_numericas == 0).sum()
porcentaje_ceros = (ceros / len(df_numericas)) * 100

resumen_ceros = pd.DataFrame({
    'Cantidad de Ceros': ceros,
    'Porcentaje (%)': porcentaje_ceros
})

# Filtrar solo columnas con ceros (opcional)
resumen_ceros = resumen_ceros[resumen_ceros['Cantidad de Ceros'] > 0]

# Ordenar de mayor a menor
resumen_ceros = resumen_ceros.sort_values(by='Porcentaje (%)', ascending=False)

print("\n=== 📊 RESUMEN DE CEROS ===\n")
print(resumen_ceros)

# =========================
# GUARDAR RESULTADO
# =========================
resumen_ceros.to_csv("resumen_ceros.csv")
print("\nArchivo 'resumen_ceros.csv' generado.")

# =========================
# GRÁFICO
# =========================
plt.figure()
resumen_ceros['Porcentaje (%)'].plot(kind='bar')

plt.title("Porcentaje de valores 0 por columna")
plt.ylabel("Porcentaje (%)")
plt.xlabel("Columnas")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()