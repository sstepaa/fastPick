# fastPick

## 🔩 Pipeline de análisis de tiempos de retiros en sucursales  

Este proyecto automatiza la recolección, limpieza y análisis de pedidos ya retirados por parte de los clientes en sucursales. A través de un pipeline semiautomático, desarrollado en Python y visualizado en Looker Studio, permite calcular cuánto tiempo tarda un cliente en retirar su producto desde el momento de la facturación.  
El objetivo final es optimizae el orden operativo en sucursal y mejorar la experiencia postventa.  
## 🔥 Objetivo del proyecto  
En particular nuestras sucursales tienen un depósito limitado y el canal de E-commerce no cuenta con un espacio propio de almacenamiento de su mercadería, es fundamental minizar el tiempo que un producto facturado permanece sin ser retirado por el cliente.  
Con este pipeline, analizamos el comportamiento real del cliente post facturación lo que permite:  
Detectar patrones de demora.    
Calcular KPIs por prooducto, familia, y en versiones futuras por sucursal.   
Tomar decisiones de gestión operativa con datos reales.  

## 🐍 Arquitectura del Pipeline  
ERP (CSV/XLSX) ➞ Google Drive ➞ Python (proceso ETL) ➞ Google Sheets ➞ Looker Studio  
### 1. Entrada de datos

Archivos semanales descargados manualmente desde el ERP.

Formato: .csv o .xlsx, ubicados en la carpeta datosRaw/ en Google Drive.

Nomenclatura: RETIROS_YYYYMMDD.

### 2. Proceso en Python

Autenticación con Google Drive mediante PyDrive2.  
Google Sheets API para lectura/escritura desde archivo maestro  

Búsqueda del archivo más reciente por nombre o fecha de modificación.

Validación: ¡¿es el archivo actualizado?!

Limpieza y transformación de los datos:

Conversión de fechas

Cálculo de días entre facturación y retiro

Flags de criticidad:

0-5 días: Normal

6-10 días: Moderado

11+ días: Crítico

Concatenación inteligente al archivo maestro (sin duplicados).

### 3. Google Sheets

Archivo maestro actualizado semanalmente con el histórico consolidado.

Usado como fuente para visualización.

### 4. Visualización en Looker Studio

Dashboard con filtros por sucursal, producto, estado de retiro.

## KPIs principales:

Promedio de días hasta el retiro

Distribución de retiros por categoría (normal, moderado, crítico)

## 🖐🏼 Mi rol  
1- Diseño y liderazgo completo del pipeline  
2- Automatización del flujo de datos con Python  
3- Conexión con APIs de Google y Google Sheets  
4- Limpieza y enriquecimiento de los reportes  
5- Modelado de KPIs  
6- Diseño de dashboard en Looker Studio  

## 🖇️ Futuras mejoras  

Dashboard comparativo por sucursal  
Normalización y georreferenciación de columnas de dirección (Calle y número) para futuros análisis geograficos y mapeo de la ciudad y alrededores  

![image](https://github.com/user-attachments/assets/abdbc562-0da4-4fa6-a2ea-fd776ef4cc58)

