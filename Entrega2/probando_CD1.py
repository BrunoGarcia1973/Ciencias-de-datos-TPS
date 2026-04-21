import pandas as pd 
import os

def cargar_dataset(ruta=None):
    """
    Carga el dataset desde la ruta especificada.
    Si no se pasa ruta, usa el archivo por defecto ubicado en el mismo directorio del script.
    """
    
    if ruta is None:
        # Ruta por defecto: mismo directorio que este script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        nombre_archivo = 'produccion-de-pozos-de-gas-y-petroleo-unificado.csv.gz'
        ruta = os.path.join(directorio_actual, nombre_archivo)

    print(f"Cargando dataset desde: {ruta}")
    try:
        df = pd.read_csv(ruta, encoding='utf-8', sep=',')
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, encoding='latin1', sep=',')
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo en:\n{ruta}")
        raise
    return df

def auditar_categoricas(df, columnas):
    """
    Imprime un informe de frecuencias y valores únicos para las columnas especificadas.
    """
    print("\n=== 📊 AUDITORÍA DE VARIABLES CATEGÓRICAS ===\n")
    for col in columnas:
        if col in df.columns:
            print(f"--- Frecuencia para: {col.upper()} ---")
            conteo = df[col].value_counts(dropna=False)
            print(conteo)
            unicos = df[col].nunique()
            print(f"📌 Total de categorías distintas: {unicos}")
            print("-" * 40 + "\n")
        else:
            print(f"⚠️ ATENCIÓN: La columna '{col}' no existe en el DataFrame.\n")

# Si se ejecuta directamente el script, hacemos la auditoría original
if __name__ == "__main__":
    df = cargar_dataset()
    columnas_a_auditar = ['cuenca', 'tipo_de_recurso', 'tipoextraccion', 'tipopozo']
    auditar_categoricas(df, columnas_a_auditar)