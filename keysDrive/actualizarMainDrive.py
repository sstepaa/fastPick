#¿Que hace esta función?
#1- Lee el historico desde Google Sheet(si existe)
#2- Concatena el DateFrame nuevo (df_nuevo) al historico
#3- Elimina duplicados columnas_clave = ['TIPO_FACTURA', 'ID_FACTURA', 'DOCUMENTO',TIPO_DE_PRODUCTO', 'PRODUCTO', 'ANULACION']
#4- Actualiza la hoja de calculo en Google drive
#5 - Guarda una ruta local por posible BackUp
import pandas as pd
import os
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials as GSCredentials
from googleapiclient.discovery import build

def exportar_main_google_sheet(df_nuevo,ruta_credenciales,nombre_hoja_google,folder_id_main,ruta_backup_local = None):

    #Autenticar
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    gsc_creds = GSCredentials.from_service_account_file(ruta_credenciales, scopes=scope)
    gs_client = gspread.authorize(gsc_creds)
    drive_service = build("drive", "v3", credentials=gsc_creds)
    
    #Asegurar incosistencias de columnas
    df_nuevo.columns = df_nuevo.columns.str.strip()
    df_nuevo = df_nuevo.loc[:, ~df_nuevo.columns.duplicated()]
    
        # --- Buscar archivo en la carpeta MAIN ---
    def buscar_hoja_en_carpeta(nombre_archivo, folder_id, drive_service):
        query = f"name = '{nombre_archivo}' and mimeType = 'application/vnd.google-apps.spreadsheet' and '{folder_id}' in parents and trashed = false"
        resultado = drive_service.files().list(q=query, fields="files(id, name)").execute()
        archivos = resultado.get("files", [])
        return archivos[0] if archivos else None
    
    archivo_encontrado = buscar_hoja_en_carpeta(nombre_hoja_google, folder_id_main, drive_service)

    
    if archivo_encontrado:
            sheet = gs_client.open_by_key(archivo_encontrado["id"])
            worksheet = sheet.get_worksheet(0)
            print(f"[INFO] Archivo encontrado en carpeta MAIN: {archivo_encontrado['name']}")
            
            data = worksheet.get_all_values()
            headers = data[0]
            values = data[1:]
            df_historial = pd.DataFrame(values, columns=headers)
            df_historial.columns = df_historial.columns.str.strip()
            df_historial = df_historial.loc[:, ~df_historial.columns.duplicated()]
    else:
        sheet = gs_client.create(nombre_hoja_google)
        worksheet = sheet.get_worksheet(0)
        df_historial = pd.DataFrame()
        print("[INFO] Archivo no encontrado. Se creó un nuevo Google Sheet.")
            
            # Mover el nuevo archivo a la carpeta MAIN
        drive_service.files().update(
            fileId=sheet.id,
            addParents=folder_id_main,
            removeParents='',
            fields='id, parents'
        ).execute()
        print("[OK] Archivo nuevo movido a carpeta MAIN.")

        # --- Unificar formato en columnas clave ---
        columnas_clave = ['TIPO_FACTURA', 'ID_FACTURA', 'DOCUMENTO', 'TIPO_DE_PRODUCTO', 'PRODUCTO', 'ANULACION']
        for col in columnas_clave:
            if col in df_nuevo.columns:
                df_nuevo[col] = df_nuevo[col].astype(str).str.strip()
            if col in df_historial.columns:
                df_historial[col] = df_historial[col].astype(str).str.strip()

        # --- Concatenar si hay historial, si no, usar solo nuevos ---
    if not df_historial.empty:
            print(f"[INFO] Registros previos: {len(df_historial)} | Nuevos: {len(df_nuevo)}")
            df_total = pd.concat([df_historial, df_nuevo], ignore_index=True)
    else:
        df_total = df_nuevo.copy()
        print(f"[INFO] No hay historial. Se usará solo el nuevo archivo ({len(df_nuevo)} filas).")

    print(f"[INFO] Total antes de deduplicar: {len(df_total)}")

    # --- Deduplicación ---
    if set(['TIPO_FACTURA', 'ID_FACTURA', 'DOCUMENTO']).issubset(df_total.columns):
        df_total.drop_duplicates(
            subset=['TIPO_FACTURA', 'ID_FACTURA', 'DOCUMENTO', 'TIPO_DE_PRODUCTO', 'PRODUCTO', 'ANULACION'],
            keep='last', inplace=True
            )
    else:
        df_total.drop_duplicates(keep='last', inplace=True)

    print(f"[INFO] Total después de deduplicar: {len(df_total)}")

        # --- Subir datos actualizados a Sheets ---
    worksheet.clear()
    set_with_dataframe(worksheet, df_total)
    print("[OK] Google Sheet actualizado con histórico consolidado.")
    
    return df_total
     
    
    
    
#Uso la función como "black box" que solo sube datos y no necesitás tocar el output.
