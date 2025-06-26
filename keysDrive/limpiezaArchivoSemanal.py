#Este script esta apuntando a automatizar el set de datos que se explotoro en el ANALISIS anterior.
import pandas as pd
import numpy as np

#Leer el archivo correcto
def leer_archivo(ruta):
    #Lee un archivo CSV o EXCEL segun la extensión que tenga el archivo
    if ruta.endswith(".csv"):
        df = pd.read_csv(ruta)
    else:
        df = pd.read_excel(ruta)
        
    return df

#1- Normalizo los nombre de COLUMNAS
def normalizar_columnas(df):
    df.columns = df.columns.str.replace(r'\s+', '_', regex=True) \
                       .str.upper() \
                       .str.normalize('NFKD') \
                       .str.encode('ascii', errors='ignore') \
                       .str.decode('utf-8')
    return df

#2- FILTRAR registros, eliminar registros de OENVIO
def filtrar_retiros(df):
    #Solo me quedo con los registros OARETI
    return df[df['ENTREGA'].str.contains('OARETI', na=False)].copy()

#3- Eliminar columnas que no son relevantes para el analisis
def eliminar_columnas_irrelevantes(df):
    columnas_eliminar = [
        'NIVEL_2','CONFORMIDAD','NO_CONFORMIDAD','HOJA_DE_RUTA','FECHA_ENTREGA','PEDIDO_MAGENTO','DEPOSITO'
    ]
    
    return df.drop(columns = columnas_eliminar, errors='ignore')

#4- DIVIDIR columnas compuestas y eliminar las originales
def dividir_columnas(df):
    # Limpiar espacios y normalizar separador
    df['FACTURA'] = df['FACTURA'].astype(str).str.strip().str.replace(r'\s*-\s*', ' - ', regex=True)
    df['ENTREGA'] = df['ENTREGA'].astype(str).str.strip().str.replace(r'\s*-\s*', ' - ', regex=True)

    # Prevenir errores si no todas las filas tienen el separador
    df[['TIPO_FACTURA', 'ID_FACTURA']] = df['FACTURA'].str.split(' - ', n=1, expand=True)
    df[['TIPO_ENTREGA', 'ID_ENTREGA']] = df['ENTREGA'].str.split(' - ', n=1, expand=True)

    # Mostrar alerta si hubo valores sin separar
    facturas_invalidas = df[df['TIPO_FACTURA'].isna() | df['ID_FACTURA'].isna()]
    entregas_invalidas = df[df['TIPO_ENTREGA'].isna() | df['ID_ENTREGA'].isna()]

    if not facturas_invalidas.empty:
        print(f"[WARN] Algunas facturas no tienen separador válido. Filas afectadas: {len(facturas_invalidas)}")
        print(facturas_invalidas[['FACTURA']].head())

    if not entregas_invalidas.empty:
        print(f"[WARN] Algunas entregas no tienen separador válido. Filas afectadas: {len(entregas_invalidas)}")
        print(entregas_invalidas[['ENTREGA']].head())

    # Eliminar columnas originales
    df = df.drop(columns=['FACTURA', 'ENTREGA'])

    # Reordenar columnas
    orden_correcto = ['NOMBRE', 'DOCUMENTO', 'TIPO_FACTURA', 'ID_FACTURA', 'TIPO_ENTREGA', 'ID_ENTREGA']
    orden_correcto += [col for col in df.columns if col not in orden_correcto]
    df = df[orden_correcto]

    return df
#5- Trato la columna ANULACIÓN
def columna_anulacion(df):
    #Esto creara una columna Boolean donde 
    #True -> anulada 
    #False -> no fue anulada.
    #Esta columna debe filtrase antes y podes sacar un porcentaje de anulaciones
    df['ANULACION'] = df['ANULACION'].notna()
    return df

#6- Trabaja unicamente en la columna fecha, para no perder ningun dato o mal parseado
def convertir_fecha_segura(columna):
    """
    Convierte una columna a fechas, detectando si son números de Excel o strings.
    """
    fechas_convertidas = pd.to_datetime(columna, errors='coerce', dayfirst=True)

    # Si hay muchas fechas NaT, intentamos convertir los valores como números de Excel
    cantidad_nat = fechas_convertidas.isna().sum()
    total = len(fechas_convertidas)

    if cantidad_nat / total > 0.2:
        print(f"[ALERTA] {cantidad_nat}/{total} fechas fallaron. Intentando como fechas Excel.")
        
        # Intentar como números de Excel (días desde 1899-12-30)
        posibles_fechas_excel = pd.to_datetime(pd.to_numeric(columna, errors='coerce'), unit='D', origin='1899-12-30')
        # Reemplazar las que fallaron con las posibles válidas
        fechas_convertidas.fillna(posibles_fechas_excel, inplace=True)

    return fechas_convertidas

#7- calcula las columnas de pre calculos
def calcular_dias_estado(df):
    df['FECHA_FACTURA'] = convertir_fecha_segura(df['FECHA_FACTURA'])
    df['FECHA_DE_MOVIMIENTO'] = convertir_fecha_segura(df['FECHA_DE_MOVIMIENTO'])

    # Control final
    if df['FECHA_FACTURA'].isna().any():
        print("[ERROR] Quedaron fechas de factura vacías tras todos los intentos.")
    if df['FECHA_DE_MOVIMIENTO'].isna().any():
        print("[ERROR] Quedaron fechas de movimiento vacías tras todos los intentos.")
    
    # Calcular días
    df['DIAS_RETIRO'] = (df['FECHA_DE_MOVIMIENTO'] - df['FECHA_FACTURA']).dt.days

    # Categorizar
    df['ESTADO_RETIRO'] = pd.cut(
        df['DIAS_RETIRO'],
        bins=[-1, 5, 10, float('inf')],
        labels=['Normal', 'Moderado', 'Crítico']
    )

    return df
#8 - Conversion segura de TIPO_DE_PRODUCTO a str
def tratar_tipo_de_producto(df):
    if 'TIPO_DE_PRODUCTO' in df.columns:
        df['TIPO_DE_PRODUCTO'] = (
            df['TIPO_DE_PRODUCTO'].astype(str).str.strip().replace([""," ","nan","None"], pd.NA)
        )
    else:
        print("[WARN] La columna 'TIPO_DE_PRODUCTO' no fue encontrada.")
    
    
    if 'PRODUCTO' in df.columns:
        df['PRODUCTO'] = (
            df['PRODUCTO'].astype(str).str.strip().replace([""," ","nan","None"], pd.NA)
        )
    else:
        print("[WARN] La columna 'PRODUCTO' no fue encontrada.")    
    
    return df
    

#9 - Exportar el archivo en formato CSV a nivel local, para tener un respaldo local
def exportar_csv(df,ruta_salida):
    #Exporta un dataFrame a CSV
    df.to_csv(
        ruta_salida,
        index=False,
        encoding='utf-8',
        date_format='%Y-%m-%d'  # Formato estándar para Looker
    )
    print(f"[OK] Archivo exportado localmente: {ruta_salida}")
    
  
#FUNCION PRINCIPAL    
    
def limpiar_archivo(ruta):
    df= leer_archivo(ruta)
    df= normalizar_columnas(df)
    df= filtrar_retiros(df)
    df= eliminar_columnas_irrelevantes(df)
    df= tratar_tipo_de_producto(df)
    df= dividir_columnas(df)
    df= columna_anulacion(df)
    df['FECHA_FACTURA'] = convertir_fecha_segura(df['FECHA_FACTURA'])
    df['FECHA_DE_MOVIMIENTO'] = convertir_fecha_segura(df['FECHA_DE_MOVIMIENTO'])
    df= calcular_dias_estado(df)
    
    return df