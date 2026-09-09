"""
cargar_datos.py - Carga del CSV con numpy (obligatorio usar np.genfromtxt).
"""
import pathlib
import numpy as np

DEFAULT_CSV = pathlib.Path(__file__).resolve().parents[1] / "data" / "dolar_observado_sii_2022_2025.csv"

def cargar_datos(ruta_csv=None):
    """
    Carga el CSV del dólar observado SII usando numpy.

    Parámetros
    ----------
    ruta_csv : str | Path | None
        Ruta al CSV. Si es None, usa data/dolar_observado_sii_2022_2025.csv

    Retorna
    -------
    data : np.ndarray estructurado con campos anio, mes, mes_num, dolar_observado_promedio_clp
    """
    if ruta_csv is None:
        ruta_csv = DEFAULT_CSV
    else:
        ruta_csv = pathlib.Path(ruta_csv)
    data = np.genfromtxt(
        ruta_csv,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8"
    )
    return data

def extraer_series(data):
    """Extrae vectores numpy útiles."""
    anios = data["anio"]
    meses = data["mes"]
    mes_num = data["mes_num"]
    valores = data["dolar_observado_promedio_clp"].astype(float)
    # etiquetas tipo 2022-01
    etiquetas = np.array([f"{a}-{m:02d}" for a, m in zip(anios, mes_num)])
    return anios, meses, mes_num, valores, etiquetas

if __name__ == "__main__":
    data = cargar_datos()
    print(f"Filas cargadas: {len(data)}")
    print(data.dtype)
    print(data[:3])
