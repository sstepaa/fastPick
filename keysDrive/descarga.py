from datetime import datetime

def descarga(archivo_drive, ruta_local_destino):
    nombre_archivo = archivo_drive['title']
    
    fecha_mod = datetime.strptime(archivo_drive['modifiedDate'][:10], "%Y-%m-%d").date()
    hoy = datetime.now().date()
    
    if fecha_mod == hoy:
        print(f"[AUTOMATICO] Descargar archivo de hoy: {nombre_archivo}\n")
        archivo_drive.GetContentFile(ruta_local_destino)
        print(f"[OK] Descarga completada: {ruta_local_destino}\n")
        return True
    else:
        print(f"[ADVERTENCIA] El archivo encontrado NO es de hoy\n")
        print(f"Archivo: {nombre_archivo} | Modificado {fecha_mod}")
        respuesta = input("¿Desea descargarlo igualmente? (s/n): ").strip().lower()
        
        if respuesta == "s":
            archivo_drive.GetContentFile(ruta_local_destino)
            print(f"[OK] Descarga completada: {ruta_local_destino}")
            return True
        else:
            print("[CANCELADO] Descarga abortada por el usuario.")
            return False