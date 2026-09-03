# Manual Técnico: Script de Organización y Traslado Recursivo de Archivos Multimedia

## 1. Descripción General del Sistema

El script desarrollado es una herramienta de automatización escrita en Python diseñada para la gestión de almacenamiento y la reestructuración de archivos multimedia en entornos **Windows**.

El programa realiza un recorrido recursivo en un directorio de origen, identifica archivos que coinciden con una lista predefinida de extensiones multimedia (imágenes, audios y vídeos), y los traslada físicamente hacia una carpeta de destino en otra unidad de disco (por ejemplo, del disco `C:` al disco `D:`).

Durante este proceso, el programa preserva de forma idéntica la **jerarquía de subcarpetas original** y genera automáticamente un **acceso directo nativo de Windows (`.lnk`)** en cada subcarpeta de origen desde la cual se extrajeron archivos, facilitando la navegación hacia la nueva ubicación.

---

## 2. Diagrama de Flujo del Algoritmo

```
               [Inicio del Programa]
                         │
        ┌────────────────┴────────────────┐
        │  Validar existencia de 'origen' │
        └────────────────┬────────────────┘
                         │
                 ¿Existe 'origen'?
               ┌─────────┴─────────┐
              Sí                   No
               │                   │
               ▼                   ▼
    [Iniciar os.walk()]     [Mostrar error y salir]
               │
               ▼
   [Para cada archivo encontrado]
               │
               ▼
     ¿Extensión multimedia?
               ┌─────────┴─────────┐
              Sí                   No
               │                   │
               ▼                   ▼
  [Calcular ruta relativa]   [Ignorar archivo]
               │
               ▼
 [Crear subcarpeta en destino]
 (os.makedirs exist_ok=True)
               │
               ▼
   [Mover archivo (shutil.move)]
               │
               ▼
  [Crear acceso directo (.lnk)]
     (vía PowerShell / WScript)
               │
               ▼
[Incrementar contador e informar]
               │
               ▼
       [Fin del Recorrido]
               │
               ▼
     [Mostrar Resumen Final]

```

---

## 3. Requisitos del Sistema y Dependencias

* **Lenguaje:** Python 3.6 o superior.
* **Sistema Operativo:** Microsoft Windows 10 / 11 (requerido para la ejecución del motor PowerShell que genera los accesos directos `.lnk`).
* **Librerías Requeridas:** Todas pertenecen a la biblioteca estándar de Python (no requieren instalación vía `pip`):
* `os`: Operaciones de sistema de archivos y manipulación de rutas.
* `shutil`: Operaciones de alto nivel sobre archivos (movimiento inter-unidad).
* `subprocess`: Ejecución de comandos del sistema operativo desde Python.



---

## 4. Estructura del Código y Análisis Módulo por Módulo

### 4.1. Importación de Módulos

```python
import os
import shutil
import subprocess

```

* **`os`**: Proporciona funciones clave como `os.walk()` para la exploración recursiva, `os.path.join()` para la construcción segura de rutas de archivo independientes del S.O., y `os.path.relpath()` para calcular rutas relativas.
* **`shutil`**: Se utiliza `shutil.move()` debido a que permite mover archivos a través de distintos volúmenes lógicos o discos físicos (operación *cross-device*), superando las limitaciones del comando atómico `os.rename()`.
* **`subprocess`**: Invoca el intérprete de mandatos de PowerShell en un hilo secundario para interactuar con la API COM `WScript.Shell` de Windows.

### 4.2. Función Auxiliar: `crear_acceso_directo()`

```python
def crear_acceso_directo(ruta_origen_carpeta, ruta_destino_carpeta):
    nombre_acceso = "Acceso a Multimedia Movidos.lnk"
    ruta_enlace = os.path.join(ruta_origen_carpeta, nombre_acceso)
    
    if not os.path.exists(ruta_enlace):
        try:
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

```

#### Fundamento Técnico:

1. **Verificación de Existencia:** Previene la sobreescritura innecesaria del acceso directo si la subcarpeta contiene múltiples archivos procesados.
2. **Automatización COM mediante PowerShell:** Crea un objeto `WScript.Shell` que instancia un acceso directo `.lnk` con la propiedad `TargetPath` apuntando a la ruta de destino.
3. **Manejo de E/S Estándar:** `stdout=subprocess.DEVNULL` y `stderr=subprocess.DEVNULL` suprimen la salida en consola de PowerShell, manteniendo la terminal limpia.

### 4.3. Exploración y Replicación de la Estructura de Directorios

```python
for carpeta, subcarpetas, archivos in os.walk(origen):
    for archivo in archivos:
        if archivo.lower().endswith(extensiones):
            origen_archivo = os.path.join(carpeta, archivo)
            
            ruta_relativa = os.path.relpath(carpeta, origen)
            destino_carpeta = os.path.join(destino, ruta_relativa)
            destino_archivo = os.path.join(destino_carpeta, archivo)

            os.makedirs(destino_carpeta, exist_ok=True)

```

#### Cálculo de Ruta Relativa:

Si la carpeta de origen es `C:\Origen` y la actual es `C:\Origen\2026\Fotos`, la llamada `os.path.relpath(carpeta, origen)` devuelve `2026\Fotos`. Al concatenar este resultado con la carpeta de destino (`D:\Destino`), se obtiene la ruta exacta de réplica: `D:\Destino\2026\Fotos`.

---

## 5. Tabla de Definición de Variables y Tipos de Datos

| Variable | Tipo de Dato | Descripción |
| --- | --- | --- |
| `origen` | `str` (Raw string) | Ruta absoluta del directorio principal a inspeccionar. |
| `destino` | `str` (Raw string) | Ruta absoluta del directorio base donde se replicará la estructura. |
| `extensiones` | `tuple` de `str` | Tupla inmutable con las extensiones de archivo permitidas en minúsculas. |
| `archivos_procesados` | `int` | Contador de control para el informe final de archivos trasladados con éxito. |
| `carpeta` | `str` | Ruta del directorio actual durante la iteración de `os.walk()`. |
| `subcarpetas` | `list` de `str` | Subdirectorios contenidos en la carpeta actual. |
| `archivos` | `list` de `str` | Nombre de los archivos presentes en la carpeta actual. |
| `ruta_relativa` | `str` | Estructura de carpetas comprendida entre `origen` y el directorio actual. |
| `destino_carpeta` | `str` | Ruta equivalente en el disco de destino donde se ubicará el archivo. |

---

## 6. Guía de Uso y Configuración

1. **Parámetros de Entrada:**
Abra el script en un editor de texto o IDE y modifique las siguientes líneas según la estructura de su equipo:
```python
origen = r"C:\TuRuta\Origen"
destino = r"D:\TuRuta\Destino"

```


2. **Ejecución:**
Ejecute el script desde la línea de comandos o terminal de su entorno de desarrollo:
```bash
python nombre_del_script.py

```


3. **Comportamiento Esperado:**
* Los archivos multimedia se moverán a la unidad de destino.
* Los archivos no multimedia (ej. `.docx`, `.pdf`) permanecerán intactos en el origen.
* En cada subcarpeta de origen donde existían multimedia, aparecerá el archivo `Acceso a Multimedia Movidos.lnk`.



---

## 7. Control de Excepciones y Consideraciones de Seguridad

* **Caracteres Especiales y Espacios:** El script utiliza sintaxis *raw string* (`r"..."`) y funciones nativas de manipulación de rutas (`os.path.join`), lo que previene fallos por espacios en blanco o acentos en las rutas de Windows.
* **Manejo de Errores en Ejecución:** El bloque `try/except` que envuelve `shutil.move()` evita que el script se interrumpa ante un archivo bloqueado por otro proceso o por falta de permisos en un archivo puntual.
* **Privilegios:** La generación de accesos directos `.lnk` mediante la interfaz COM de `WScript.Shell` funciona dentro de los privilegios de un usuario estándar, **sin requerir elevación a modo Administrador**.