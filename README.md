# Descargador de Pinterest (para VS Code)

Script en Python que descarga imágenes de tableros o pines de Pinterest
(públicos o privados/guardados) a carpetas locales en tu computadora.

Usa por debajo la librería open source [`pinterest-dl`](https://github.com/sean1832/pinterest-dl).

> ⚠️ Este es un proyecto no oficial. No está afiliado a Pinterest. Úsalo solo
> para descargar contenido de tu propia cuenta o contenido público, respetando
> los términos de servicio de Pinterest.

## 1. Requisitos

- Tener **Python 3.10 o superior** instalado. Verifica en la terminal de VS Code:
  ```
  python3 --version
  ```
  Si no lo tienes, descárgalo de https://www.python.org/downloads/

- Tener **Visual Studio Code** con la extensión de Python instalada.

## 2. Instalación

1. Descarga esta carpeta completa (o clónala) y ábrela en VS Code
   (`Archivo > Abrir carpeta...`).
2. Abre una terminal en VS Code (`Terminal > Nueva terminal`).
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
   (En Mac/Linux puede que necesites `pip3` en vez de `pip`).

## 3. Uso

Corre el script desde la terminal de VS Code:

```
python pinterest_downloader.py
```

Verás un menú interactivo:

```
1) Iniciar sesión (para tableros/pines privados)
2) Descargar un TABLERO completo
3) Descargar un PIN (y opcionalmente relacionados)
4) Salir
```

### Descargar un tablero público
Elige la opción **2**, pega la URL del tablero
(ej. `https://www.pinterest.com/usuario/nombre-tablero/`), responde "n" a si es
privado, y elige el nombre de carpeta. Las imágenes quedarán en:

```
Pinterest_Descargas/<nombre-que-elegiste>/
```

### Descargar un tablero privado o tus pines guardados
1. Primero elige la opción **1** del menú para iniciar sesión.
   - Si ya tienes **Firefox** con tu sesión de Pinterest abierta, el script
     puede leer las cookies directamente de ahí (opción recomendada, no
     necesita nada extra).
   - Si no, se abrirá una ventana de navegador automatizado para que inicies
     sesión manualmente (requiere `pip install "pinterest-dl[browser]"` y
     `playwright install chromium`, el script te avisará si falta).
2. Luego elige la opción **2** o **3**, y responde "s" cuando pregunte si es
   contenido privado.

## 4. ¿Dónde quedan las imágenes?

Todo se guarda dentro de la carpeta `Pinterest_Descargas/`, organizada en
subcarpetas por cada tablero o pin que descargues. Puedes verlas directamente
en el explorador de archivos de VS Code (panel izquierdo).

## 5. Notas

- Para "descargar todo el tablero" el script pide hasta 10,000 imágenes por
  defecto, así que en la práctica trae el tablero completo.
- Si un tablero es muy grande, la descarga puede tardar varios minutos.
- Si algo falla, revisa el mensaje en la terminal: casi siempre es porque la
  URL está mal copiada o falta iniciar sesión para contenido privado.
