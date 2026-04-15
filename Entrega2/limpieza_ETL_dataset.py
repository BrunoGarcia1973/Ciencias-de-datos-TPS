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

import matplotlib.pyplot as plt
import seaborn as sns

print("\n=== 🔍 1. ANÁLISIS DE CALIDAD DE DATOS Y ESTADÍSTICO ===")

# Revisar la cantidad de valores nulos por columna
print("\n--- Valores Faltantes (Nulos) por columna ---")
nulos = df.isnull().sum()
nulos_filtrados = nulos[nulos > 0]
if not nulos_filtrados.empty:
    print(nulos_filtrados)
else:
    print("No se encontraron valores nulos.")

# Análisis estadístico de las variables numéricas (producción)
# Ayuda a identificar outliers (valores atípicos) o errores (ej. producción negativa)
print("\n--- Estadísticas Descriptivas (Variables Numéricas) ---")
# Filtramos solo columnas numéricas que típicamente están en este dataset
cols_numericas = [col for col in df.columns if 'prod' in col.lower() or col in ['cantidad_pozos']]
if cols_numericas:
    print(df[cols_numericas].describe().round(2))

print("\n=== 🛠️ 2. ESTRATEGIA DE TRANSFORMACIÓN Y LIMPIEZA ===")

# Estrategia 1: Eliminación de registros completamente duplicados
duplicados = df.duplicated().sum()
if duplicados > 0:
    df = df.drop_duplicates()
    print(f"✅ Se eliminaron {duplicados} registros duplicados.")
else:
    print("✅ No hay registros duplicados exactos.")

# Estrategia 2: Imputación de nulos
# Si hay producción con valor nulo (NaN), lo razonable estadísticamente es asignarle 0
for col in cols_numericas:
    if df[col].isnull().any():
        df[col] = df[col].fillna(0)
        print(f"✅ Nulos en '{col}' reemplazados por 0.")

# Estrategia 3: Filtrar datos inconsistentes (Ejemplo: producción negativa)
# Eliminamos filas donde la producción de gas o petróleo sea menor a 0 (si las hay)
filas_iniciales = len(df)
for col in ['prod_pet', 'prod_gas']:
    if col in df.columns:
        df = df[df[col] >= 0]
if filas_iniciales != len(df):
    print(f"✅ Se eliminaron {filas_iniciales - len(df)} registros con producción negativa (datos inconsistentes).")

print(f"\nDataset limpio preparado. Total de filas finales: {len(df)}")


print("\n=== 📈 3. ANÁLISIS DE VARIABLES (VISUALIZACIONES) ===")
# Configuración estética de los gráficos
sns.set_theme(style="whitegrid")

# --- Gráfico 1: Validando Hipótesis 1 (Distribución por Cuenca) ---
if 'cuenca' in df.columns:
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, y='cuenca', order=df['cuenca'].value_counts().index, palette='viridis')
    plt.title('Distribución de Registros por Cuenca', fontsize=14)
    plt.xlabel('Cantidad de Registros')
    plt.ylabel('Cuenca')
    plt.tight_layout()
    # Descomentar la siguiente línea para mostrar el gráfico (la dejamos como guardado para el proyecto)
    plt.savefig('analisis_cuencas.png')
    print("📊 Gráfico de cuencas generado y guardado como 'analisis_cuencas.png'.")

# --- Gráfico 2: Validando Hipótesis 2 (Producción Promedio según Recurso) ---
# Requiere que existan las columnas de producción y tipo de recurso
if 'tipo_de_recurso' in df.columns and 'prod_pet' in df.columns and 'prod_gas' in df.columns:
    # Agrupamos los datos
    produccion_recurso = df.groupby('tipo_de_recurso')[['prod_pet', 'prod_gas']].mean().reset_index()
    
    # Preparamos los datos para que Seaborn los entienda fácilmente (formato "melt")
    prod_melt = pd.melt(produccion_recurso, id_vars=['tipo_de_recurso'], 
                        value_vars=['prod_pet', 'prod_gas'], 
                        var_name='Tipo de Producción', value_name='Producción Promedio')
    
    plt.figure(figsize=(8, 6))
    sns.barplot(data=prod_melt, x='tipo_de_recurso', y='Producción Promedio', hue='Tipo de Producción')
    plt.title('Producción Promedio de Gas y Petróleo por Tipo de Recurso', fontsize=14)
    plt.xlabel('Tipo de Recurso (Shale vs Tight)')
    plt.ylabel('Volumen Promedio')
    plt.tight_layout()
    plt.savefig('produccion_por_recurso.png')
    print("📊 Gráfico de producción por recurso guardado como 'produccion_por_recurso.png'.")

print("\n¡Proceso de la Segunda Entrega completado con éxito! 🎉")