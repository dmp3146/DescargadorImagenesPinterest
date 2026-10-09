#!/usr/bin/env python3
"""
Descargador de Pinterest
-------------------------
Descarga imágenes de tableros o pines de Pinterest (públicos o privados)
usando la librería 'pinterest-dl'.

Cambios en esta versión:
  1) Ya NO ejecuta "pinterest-dl.exe" (Windows lo bloquea con el Control de
     aplicaciones, error WinError 4551). Ahora llama al paquete directamente
     desde Python: pinterest_dl.cli:main.
  2) Ya NO reinstala cada vez. Comprueba la instalación con importlib, sin
     ejecutar ningún .exe.
  3) Revisa al inicio que tu Python tenga SSL. Sin SSL no se puede descargar
     nada de internet (pasa con el Python de uv).
  4) Si Brave pide permisos de administrador para leer cookies, ahora puedes
     importar un cookies.json exportado con la extensión Cookie-Editor.
"""

import ctypes
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DOWNLOADS_DIR = BASE_DIR / "Pinterest_Descargas"
COOKIES_FILE = BASE_DIR / "cookies.json"

# Código que se pasa a "python -c" para ejecutar pinterest-dl sin usar el .exe
_LANZADOR = (
    "import sys; sys.argv[0] = 'pinterest-dl'; "
    "from pinterest_dl.cli import main; sys.exit(main())"
)


def comando_pinterest_dl() -> list[str]:
    """Comando para invocar pinterest-dl a través de Python (sin .exe)."""
    return [sys.executable, "-c", _LANZADOR]


def run(cmd: list[str], mostrar: str | None = None) -> int:
    """Ejecuta un comando y muestra su salida en vivo."""
    print(f"\n$ {mostrar or ' '.join(cmd)}\n")
    try:
        return subprocess.run(cmd).returncode
    except OSError as e:
        print(f"⚠️  Windows no dejó ejecutar el comando: {e}")
        return 1


def run_pinterest_dl(args: list[str]) -> int:
    return run(comando_pinterest_dl() + args, mostrar="pinterest-dl " + " ".join(args))


def paquete_instalado(nombre: str) -> bool:
    return importlib.util.find_spec(nombre) is not None


def tiene_ssl() -> bool:
    try:
        import ssl  # noqa: F401
        return True
    except ImportError:
        return False


def es_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def verificar_entorno():
    """Revisa SSL y dependencias. Instala solo lo que realmente falte."""
    if not tiene_ssl():
        print(
            "\n⚠️  Este Python NO tiene soporte SSL (módulo 'ssl').\n"
            "   Sin SSL no se puede conectar a Pinterest ni instalar paquetes nuevos.\n"
            "   Solución: instala Python desde https://www.python.org/downloads/\n"
            "   (marca 'Add Python to PATH') y en VS Code elige ese intérprete con\n"
            "   Ctrl+Shift+P → 'Python: Select Interpreter'.\n"
        )

    faltan = []
    if not paquete_instalado("pinterest_dl"):
        faltan.append("pinterest-dl[browser]")
    if not paquete_instalado("browser_cookie3"):
        faltan += ["browser-cookie3", "pycryptodome", "pywin32"]

    if faltan:
        print(f"Faltan paquetes: {', '.join(faltan)}. Instalando...")
        run([sys.executable, "-m", "pip", "install", *faltan])
        if not paquete_instalado("pinterest_dl"):
            print("⚠️  No se pudo instalar 'pinterest-dl'. Revisa el aviso de SSL de arriba.")
            sys.exit(1)


def _guardar_cookies(cookies: list[dict]):
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


def login_desde_brave() -> bool:
    """Lee las cookies de pinterest.com de Brave (puede requerir administrador)."""
    try:
        import browser_cookie3
    except ImportError:
        print("Falta 'browser_cookie3'. Instálalo con: python -m pip install browser-cookie3")
        return False

    print("\nLeyendo la sesión de Pinterest de Brave...")
    try:
        cj = browser_cookie3.brave(domain_name="pinterest.com")
    except Exception as e:
        print(f"⚠️  No se pudieron leer las cookies de Brave: {e}")
        if not es_admin():
            print(
                "   Brave cifra las cookies y Windows exige permisos de administrador.\n"
                "   Opción A: cierra VS Code, ábrelo con clic derecho → 'Ejecutar como\n"
                "             administrador' y repite esta opción.\n"
                "   Opción B: usa la opción 2 del menú (importar cookies exportadas)."
            )
        return False

    cookies = []
    for c in cj:
        cookie = {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path or "/",
            "secure": bool(c.secure),
            "httpOnly": False,
        }
        if c.expires:
            cookie["expiry"] = int(c.expires)
        cookies.append(cookie)

    if not cookies:
        print(
            "⚠️  No encontré cookies de pinterest.com en Brave.\n"
            "   Abre pinterest.com en Brave, inicia sesión y vuelve a intentar."
        )
        return False

    _guardar_cookies(cookies)
    print(f"✅ Cookies guardadas en: {COOKIES_FILE} ({len(cookies)} cookies)")
    return True


def importar_cookies_exportadas():
    """
    Convierte un archivo exportado con la extensión 'Cookie-Editor'
    (botón Export → JSON) al formato que usa pinterest-dl.
    """
    print(
        "\nPasos:\n"
        "  1) En Brave instala la extensión 'Cookie-Editor'.\n"
        "  2) Entra a pinterest.com (con tu sesión iniciada).\n"
        "  3) Abre Cookie-Editor → Export → JSON (copia al portapapeles).\n"
        "  4) Pega eso en un archivo de texto y guárdalo, por ejemplo, como\n"
        "     cookies_exportadas.json\n"
    )
    ruta = input("Ruta del archivo exportado (puedes arrastrarlo aquí): ").strip().strip('"')
    if not ruta:
        return
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        print(f"⚠️  No pude leer el archivo: {e}")
        return

    cookies = []
    for c in datos:
        cookie = {
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain", ".pinterest.com"),
            "path": c.get("path", "/"),
            "secure": bool(c.get("secure", True)),
            "httpOnly": bool(c.get("httpOnly", False)),
        }
        exp = c.get("expirationDate") or c.get("expiry") or c.get("expires")
        if exp:
            cookie["expiry"] = int(exp)
        if cookie["name"] and cookie["value"] is not None:
            cookies.append(cookie)

    if not cookies:
        print("⚠️  El archivo no tenía cookies válidas.")
        return

    _guardar_cookies(cookies)
    print(f"✅ Cookies importadas a: {COOKIES_FILE} ({len(cookies)} cookies)")


def login_manual():
    """Respaldo: login en una ventana de Chromium aparte (playwright)."""
    print(
        "\nSe abrirá una ventana de Chromium aparte para iniciar sesión.\n"
        "No es tu Brave, no hace falta cerrar nada.\n"
    )
    run([sys.executable, "-m", "playwright", "install", "chromium"])
    codigo = run_pinterest_dl(["login", "-o", str(COOKIES_FILE), "--headful"])

    if codigo == 0 and COOKIES_FILE.exists():
        print(f"\n✅ Cookies guardadas en: {COOKIES_FILE}")
    else:
        print("\n⚠️  No se pudo completar el login manual.")


def hacer_login():
    if not login_desde_brave():
        r = input("\n¿Probar el login manual en una ventana aparte? (s/n): ").strip().lower()
        if r == "s":
            login_manual()


def descargar(url: str, num_imagenes: int, usar_cookies: bool, nombre_carpeta: str | None):
    carpeta_salida = DOWNLOADS_DIR / (nombre_carpeta or "tablero")
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    args = ["scrape", url, "-o", str(carpeta_salida), "-n", str(num_imagenes)]

    if usar_cookies:
        if not COOKIES_FILE.exists():
            print("\n⚠️  No encuentro cookies.json. Primero usa la opción 1 o 2 del menú.")
            return
        args += ["-c", str(COOKIES_FILE)]

    codigo = run_pinterest_dl(args)

    if codigo == 0:
        print(f"\n✅ Listo. Imágenes guardadas en: {carpeta_salida}")
    else:
        print(
            "\n⚠️  Algo falló. Revisa que la URL sea correcta y, si es contenido\n"
            "   privado, que hayas cargado tus cookies (opción 1 o 2)."
        )


def menu():
    print("=" * 60)
    print("  DESCARGADOR DE PINTEREST")
    print("=" * 60)

    verificar_entorno()

    while True:
        print(
            "\n¿Qué quieres hacer?\n"
            "  1) Leer la sesión de Pinterest desde Brave (privados)\n"
            "  2) Importar cookies exportadas con Cookie-Editor (privados)\n"
            "  3) Descargar un TABLERO completo\n"
            "  4) Descargar un PIN (y opcionalmente relacionados)\n"
            "  5) Salir\n"
        )
        opcion = input("Elige una opción (1-5): ").strip()

        if opcion == "1":
            hacer_login()

        elif opcion == "2":
            importar_cookies_exportadas()

        elif opcion == "3":
            url = input("\nPega la URL del tablero: ").strip()
            if not url:
                continue
            es_privado = input("¿Es privado o de tu cuenta? (s/n): ").strip().lower() == "s"
            nombre = input("Nombre de la carpeta (Enter = nombre del tablero): ").strip()
            if not nombre:
                nombre = url.rstrip("/").split("/")[-1] or "tablero"
            descargar(url, num_imagenes=10000, usar_cookies=es_privado, nombre_carpeta=nombre)

        elif opcion == "4":
            url = input("\nPega la URL del pin: ").strip()
            if not url:
                continue
            es_privado = input("¿Es privado o de tu cuenta? (s/n): ").strip().lower() == "s"
            try:
                cantidad = int(input("¿Cuántas imágenes en total (pin + relacionados)? [1]: ").strip() or "1")
            except ValueError:
                cantidad = 1
            nombre = input("Nombre de la carpeta (Enter = 'pin'): ").strip() or "pin"
            descargar(url, num_imagenes=cantidad, usar_cookies=es_privado, nombre_carpeta=nombre)

        elif opcion == "5":
            print("¡Listo! 👋")
            break

        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()