from quickStar import login #Importo la funcion Login
from buscarArchivos import buscar_archivo_drive #Importo la funcion busquedad
from config import * # Importo sus credenciales
from limpiezaArchivoSemanal import limpiar_archivo, exportar_csv
from subirArchivoClean import subir_archivo_hub
from actualizarMainDrive import exportar_main_google_sheet

from descarga import descarga

import pandas as pd
import os


#Primer modulo solo conectara visual studio con nuestra nube almacen (google drive)
drive = login(CLIENT_SECRETS_FILE, CREDENTIALS_FILE)

#Segundo modulo se encarga de buscar el ultimo archivo que se subio a la carpeta datosRaw en nuestra nube
archivo = buscar_archivo_drive(drive, FOLDER_IDS['datosRaw'])

#Tercer modulo descargar el archivo encontrado, este codigo esta hecho para descargarse automaticamente si es el mismo que la fecha actual y si no es identico a la fecha actual, te va a preguntar si deseas descargarlo
os.makedirs(CARPETA_LOCAL_CRUDOS, exist_ok=True)

if archivo:
    ruta_local = os.path.join(CARPETA_LOCAL_CRUDOS, f"temp_{archivo['title']}")
    if descarga(archivo, ruta_local):
        print("[INFO] Archivo listo para procesamiento\n")
    else:
        print("[STOP] No se descargó ningún archivo. Finalizando pipeline\n")
else:
    print("[ERROR] No se encontró ningún archivo para descargar")
    
# ---------- En este punto tendria que actualizar en una decision, si llevo a cabo decir N, y no bajar archivo - proximo Update -------------
    
#Cuarto modulo, limpia el archivo descargado
df_limpio = limpiar_archivo(ruta_local) #Ruta_local contiene el ultimo archivo que se descargo

#Quinto modulo, construye ruta y nombre para el archivo limpio
nombre_archivo_limpio = f"limpio_{archivo['title'].replace('.xlsx', '.csv')}"
ruta_salida = os.path.join(CARPETA_LOCAL_LIMPIO, nombre_archivo_limpio)

# 6. Exportar archivo limpio localmente
os.makedirs(CARPETA_LOCAL_LIMPIO, exist_ok=True)
exportar_csv(df_limpio, ruta_salida)

print(f"[OK] Archivo limpio guardado en: {ruta_salida}")

# Septimo modulo, subir archivo al HUB(google drive)
subir_archivo_hub(
    drive=drive,
    ruta_local=ruta_salida,
    nombre_archivo= nombre_archivo_limpio,
    folder_id=FOLDER_IDS['datosClean']
)

#Octavo modulo - actualizar main local y Google Sheet
#ARCHIVO_MAIN_LOCAL = "main_temp.csv"#Capturo la variable

exportar_main_google_sheet(
    df_nuevo=df_limpio,
    ruta_credenciales=SERVICE_ACCOUNT_CREDENTIALS,
    nombre_hoja_google=GOOGLE_SHEET_NAME,
    folder_id_main= FOLDER_IDS['main']
)






