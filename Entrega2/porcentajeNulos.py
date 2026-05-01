import pandas as pd
import matplotlib.pyplot as plt
import os

from probando_CD1 import auditar_categoricas

# =========================
# CARGA DE DATOS (RUTA CORRECTA)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ruta = os.path.join(BASE_DIR, "..", "..", "csv_limpio", "salida.csv")

print("📂 Ruta usada:", os.path.abspath(ruta))
print("📄 Existe archivo:", os.path.exists(ruta))

df = pd.read_csv(ruta)

print("Shape del dataset:", df.shape)

# =========================
# AUDITORÍA CATEGÓRICAS
# =========================
columnas_a_auditar = ['cuenca', 'tipo_de_recurso', 'tipoextraccion', 'tipopozo']
auditar_categoricas(df, columnas_a_auditar)

# =========================
# CÁLCULO DE NULOS
# =========================
nulos = df.isnull().sum()
porcentaje_nulos = (nulos / len(df)) * 100

resumen_nulos = pd.DataFrame({
    'Cantidad de Nulos': nulos,
    'Porcentaje (%)': porcentaje_nulos
})

# Filtrar solo columnas con nulos
resumen_nulos = resumen_nulos[resumen_nulos['Cantidad de Nulos'] > 0]

# Ordenar
resumen_nulos = resumen_nulos.sort_values(by='Porcentaje (%)', ascending=False)

print("\n=== 📊 RESUMEN DE NULOS ===\n")
print(resumen_nulos)

# =========================
# GUARDAR RESULTADO
# =========================
resumen_nulos.to_csv("resumen_nulos.csv", index=True)
print("\nArchivo 'resumen_nulos.csv' generado.")

# =========================
# GRÁFICO (solo si hay datos)
# =========================
if resumen_nulos.empty:
    print("\n⚠️ No hay valores nulos en el dataset. No se genera gráfico.")
else:
    plt.figure()
    resumen_nulos['Porcentaje (%)'].plot(kind='bar')

    plt.title("Porcentaje de valores nulos por columna")
    plt.ylabel("Porcentaje (%)")
    plt.xlabel("Columnas")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()