def subir_archivo_hub(drive,ruta_local,nombre_archivo,folder_id):
    #Sube el archivo limpio a google drive, al ID de la carpeta que usted le pasa por parametro
    #Parametro drive: sesión autenticada de Pydrive
    #ruta_local: ruta completa del archivo CSV limpio
    #nombre_archivo: nombre del archivo en drive
    #folder_id: Id de la carpeta donde se guardara el CSV en google drive
    
    #1- Busca si ya existe un archivo con ese nombre
    query = f"'{folder_id}' in parents and title='{nombre_archivo}' and trashed=false"
    archivos_existentes = drive.ListFile({'q': query}).GetList()
    
    for archivo in archivos_existentes:
        print(f"[INFO] Eliminando archivo existente en Drive: {archivo['title']}")
        archivo.Delete()
        
    #2- Crear y subir el nuevo archivo
    nuevo_archivo = drive.CreateFile({
        'title': nombre_archivo,
        'parents': [{'id':folder_id}]
    })
    
    nuevo_archivo.SetContentFile(ruta_local)
    nuevo_archivo.Upload()
    
    print(f"[OK] Archivo subido a Drive: {nombre_archivo}")
