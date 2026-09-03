# ============================================================
# MOVIMIENTO DE ARCHIVOS MULTIMEDIA
# ============================================================
#
# ¿QUÉ HACE ESTE SCRIPT?
#
# Este programa recorre una carpeta y todas sus subcarpetas
# para localizar determinados archivos multimedia.
#
# Los archivos encontrados son MOVIDOS a otra ubicación,
# conservando la misma estructura de carpetas que tenían
# originalmente.
#
#Finalmente, crea un enlace en la subcarpeta de origen, apuntando 
#al destino donde fue movido el archivo multimedia
#
# IMPORTANTE:
# - El programa MUEVE los archivos, no los copia.
# - Los archivos originales desaparecen de la carpeta de origen
#   después de realizarse correctamente el movimiento.
# - Solo se procesan las extensiones indicadas en la variable
#   "extensiones".
# ============================================================


# ------------------------------------------------------------
# IMPORTAR MÓDULOS
# ------------------------------------------------------------

# "os" es un módulo de Python que permite trabajar con el
# sistema operativo: rutas, carpetas, archivos, etc.
import os

# "shutil" contiene funciones para realizar operaciones
# sobre archivos y carpetas, como copiar o mover archivos.
import shutil

# "subprocess" permite ejecutar comandos del sistema (PowerShell)
import subprocess


# ------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS Y EXTENSIONES
# ------------------------------------------------------------

# ------------------------------------------------------------
# DEFINIR LA CARPETA DE ORIGEN
# ------------------------------------------------------------

# Esta variable contiene la carpeta principal donde Python
# comenzará a buscar los archivos.
#
# El programa también recorrerá todas las subcarpetas que
# existan dentro de esta ubicación.
#
# La letra "r" antes de las comillas significa "raw string".
# Se utiliza para que Python interprete correctamente las
# barras invertidas "\" utilizadas en las rutas de Windows.
origen = r"C:\Users\chira\Documents\Contratos y Convenios\LS\LS 2026"


# ------------------------------------------------------------
# DEFINIR LA CARPETA DE DESTINO
# ------------------------------------------------------------

# Esta variable indica la ubicación donde se colocarán
# los archivos encontrados.
destino = r"D:\Productos\LS 2026"


# ------------------------------------------------------------
# DEFINIR LAS EXTENSIONES QUE SE BUSCARÁN
# ------------------------------------------------------------

# Aquí se indican los tipos de archivos que el programa
# debe localizar y mover.
#
# En este caso se procesarán archivos de imagen y vídeo:
#
# .jpg  -> imagen JPEG
# .jpeg -> imagen JPEG
# .png  -> imagen PNG
# .arw	extension de sony
# .dng estandar abierto y universal de raw
# .mp4  -> vídeo MP4
# .mov  -> vídeo MOV
# .avi  -> vídeo AVI
# .mkv  -> vídeo MKV
# .mp3  -> audio mp3
# .wav  -> audio wav
#
# Los archivos con otras extensiones, por ejemplo .pdf,
# .docx o .xlsx, serán ignorados.
extensiones = (".jpg", ".jpeg", ".png", ".arw", ".dng", ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav")


# ------------------------------------------------------------
# FUNCIÓN AUXILIAR: CREAR ACCESO DIRECTO (.LNK)
# ------------------------------------------------------------

def crear_acceso_directo(ruta_origen_carpeta, ruta_destino_carpeta):
    """
    Crea un acceso directo nativo de Windows (.lnk) en la carpeta de origen 
    que apunta a la carpeta de destino donde se movieron los archivos.
    Utiliza PowerShell para evitar requerir permisos de Administrador.
    """
    nombre_acceso = "Acceso a Multimedia Movidos.lnk"
    ruta_enlace = os.path.join(ruta_origen_carpeta, nombre_acceso)
    
    # Solo crea el acceso directo si aún no existe en esa subcarpeta
    if not os.path.exists(ruta_enlace):
        try:
            # Comando de PowerShell para crear un acceso directo .lnk
            ps_script = (
                f"$WshShell = New-Object -ComObject WScript.Shell; "
                f"$Shortcut = $WshShell.CreateShortcut('{ruta_enlace}'); "
                f"$Shortcut.TargetPath = '{ruta_destino_carpeta}'; "
                f"$Shortcut.Save()"
            )
            subprocess.run(["powershell", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   [ENLACE CREADO] -> {nombre_acceso}")
        except Exception as e:
            print(f"   [ERROR AL CREAR ENLACE] -> {e}")


# ------------------------------------------------------------
# VALIDACIÓN PREVIA
# ------------------------------------------------------------
if not os.path.exists(origen):
    print(f"ERROR: La ruta de origen no existe -> {origen}")
    exit()

archivos_procesados = 0

print("Iniciando la búsqueda y movimiento de archivos...\n")


# ------------------------------------------------------------
# RECORRER CARPETAS
# ------------------------------------------------------------

# os.walk() permite recorrer una carpeta de manera recursiva.
#
# Esto significa que no solamente revisará la carpeta "origen",
# sino también todas las carpetas y subcarpetas que encuentre
# dentro de ella.
#
# En cada recorrido, os.walk() proporciona tres elementos:
#
#   carpeta      -> ruta de la carpeta que se está revisando.
#   subcarpetas  -> lista de subcarpetas encontradas.
#   archivos     -> lista de archivos encontrados.
#
for carpeta, subcarpetas, archivos in os.walk(origen):
    for archivo in archivos:
        # Verificar extensión
        if archivo.lower().endswith(extensiones):
            origen_archivo = os.path.join(carpeta, archivo)
            
            # Construir rutas de destino
            ruta_relativa = os.path.relpath(carpeta, origen)
            destino_carpeta = os.path.join(destino, ruta_relativa)
            destino_archivo = os.path.join(destino_carpeta, archivo)

            # Crear estructura de directorios en el destino
            os.makedirs(destino_carpeta, exist_ok=True)

            if os.path.exists(origen_archivo):
                try:
                    # Mover archivo (funciona entre diferentes unidades C: -> D:)
                    shutil.move(origen_archivo, destino_archivo)
                    print(f"[MOVIDO] {archivo} -> {destino_carpeta}")
                    archivos_procesados += 1

                    # --------------------------------------------------------
                    # CREAR HIPERVÍNCULO EN LA CARPETA ORIGEN
                    # --------------------------------------------------------
                    crear_acceso_directo(carpeta, destino_carpeta)

                except Exception as e:
                    print(f"[ERROR] No se pudo mover {archivo}: {e}")
            else:
                print(f"[NO ENCONTRADO] {origen_archivo}")


# ------------------------------------------------------------
# RESUMEN FINAL
# ------------------------------------------------------------
print("\n" + "="*40)
if archivos_procesados == 0:
    print("No se encontró ningún archivo con las extensiones especificadas.")
else:
    print(f"Proceso finalizado. Total de archivos movidos: {archivos_procesados}")
print("="*40)