from datetime import datetime
import re

def buscar_archivo_drive(drive, folder_id):
    fecha_actual_obj = datetime.now()
    fecha_actual_str = fecha_actual_obj.strftime("%Y%m%d")
    fecha_actual_date = fecha_actual_obj.date()

    print(f"[INFO] Buscando archivo con fecha: {fecha_actual_obj.strftime('%Y-%m-%d')}")

    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    file_list = drive.ListFile({'q': query}).GetList()

    candidatos_con_fecha = []
    todos_los_archivos = []

    for file in file_list:
        nombre = file['title']
        modificado_str = file['modifiedDate'][:10]
        fecha_mod = datetime.strptime(modificado_str, "%Y-%m-%d").date()

        todos_los_archivos.append((file, fecha_mod))

        match = re.search(r'(20\d{2})[-_]?(\d{2})[-_]?(\d{2})', nombre)
        if match:
            fecha_en_nombre = f"{match.group(1)}{match.group(2)}{match.group(3)}"
            if fecha_en_nombre == fecha_actual_str or fecha_mod == fecha_actual_date:
                print(f"[MATCH] Archivo: {nombre} | Fecha nombre/modificado: {fecha_en_nombre} / {fecha_mod}")
                candidatos_con_fecha.append((file, fecha_mod))

    if candidatos_con_fecha:
        candidatos_con_fecha.sort(key=lambda x: x[1], reverse=True)
        seleccionado = candidatos_con_fecha[0][0]
        print(f"[OK] Archivo seleccionado por fecha: {seleccionado['title']}")
        return seleccionado
    else:
        print("[WARN] No se encontró archivo para la fecha actual. Buscando el último archivo disponible...")
        if not todos_los_archivos:
            print("[ERROR] No hay archivos disponibles en la carpeta.")
            return None
        todos_los_archivos.sort(key=lambda x: x[1], reverse=True)
        seleccionado = todos_los_archivos[0][0]
        print(f"[OK] Archivo más reciente encontrado: {seleccionado['title']}")
        return seleccionado