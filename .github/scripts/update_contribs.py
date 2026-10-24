"""Actualiza el contador de contribuciones en README.md.

Lee el número que muestra el perfil público de GitHub
("N contributions in the last year"), que incluye las privadas.
Si no logra leerlo, o si cae más de un 30 % frente al actual, no toca nada.
Marcadores en el README: <!--contribs-->N<!--/contribs--> y <!--fecha-->...<!--/fecha-->.
"""
import datetime
import re
import sys
import urllib.request

USER = "GuillermoEstefanPuello"
FILE = "README.md"
CAIDA_MAXIMA = 0.30
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
RE_NUM = re.compile(r"(<!--contribs-->)([\d,.]+)(<!--/contribs-->)")
RE_FECHA = re.compile(r"(<!--fecha-->)[^<]*(<!--/fecha-->)")


def aviso(msg):
    print(f"::warning::{msg}")


def leer_perfil():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "text/html",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        page = r.read().decode("utf-8", "replace")
    texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
    m = re.search(r"([\d,]+) contributions? in the last year", texto, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    dias = re.findall(r"(\d+) contributions? on ", texto, re.I)
    return sum(int(d) for d in dias) if dias else None


def main():
    with open(FILE, encoding="utf-8") as f:
        md = f.read()
    m = RE_NUM.search(md)
    actual = int(re.sub(r"\D", "", m.group(2))) if m else 0

    try:
        total = leer_perfil()
    except Exception as e:  # noqa: BLE001
        aviso(f"No se pudo leer el perfil: {e}")
        return 0
    if not total:
        aviso("Sin dato confiable; se deja el número anterior.")
        return 0
    if actual and total < actual * (1 - CAIDA_MAXIMA):
        aviso(f"Lectura sospechosa: {total} vs actual {actual}. No se actualiza.")
        return 0

    rd = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4)
    fecha = f"{rd.day} de {MESES[rd.month - 1]} de {rd.year}"
    nuevo = RE_NUM.sub(lambda x: f"{x.group(1)}{total:,}{x.group(3)}", md)
    nuevo = RE_FECHA.sub(lambda x: f"{x.group(1)}{fecha}{x.group(2)}", nuevo)
    aviso(f"Leído {total}; actual {actual}.")
    if nuevo != md:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(nuevo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
