"""
anualidad.py - Variacion enero -> diciembre por año con error propagado (A4).
"""
import numpy as np
import pathlib
import csv

try:
    from src.cargar_datos import cargar_datos, extraer_series
    from src.errores import redondear_sig, error_absoluto, error_relativo, evaluar_delta
except ImportError:
    from cargar_datos import cargar_datos, extraer_series
    from errores import redondear_sig, error_absoluto, error_relativo, evaluar_delta


def variacion_anual(sig=2, ruta_csv=None):
    """
    Para cada año 2022-2025 calcula Delta = Diciembre - Enero con propagacion.
    Retorna lista de dicts ordenables por Er.
    """
    data = cargar_datos(ruta_csv)
    resultados = []
    for anio in sorted(set(data["anio"])):
        mask = data["anio"] == anio
        sub = data[mask]
        # enero mes_num 1, diciembre 12
        try:
            enero_real = float(sub[sub["mes_num"] == 1]["dolar_observado_promedio_clp"][0])
            dici_real = float(sub[sub["mes_num"] == 12]["dolar_observado_promedio_clp"][0])
        except IndexError:
            continue
        r = evaluar_delta(enero_real, dici_real, sig=sig)
        r["anio"] = int(anio)
        resultados.append(r)
    # ordenar por menor Er (mas confiable primero)
    resultados.sort(key=lambda x: x["er_delta_pct"])
    return resultados


def main():
    out_dir = pathlib.Path(__file__).resolve().parents[1] / "outputs"
    out_dir.mkdir(exist_ok=True)

    for sig in [2, 3]:
        print(f"\n=== A4 Anualidad (variacion enero->diciembre) {sig} cifras ===")
        res = variacion_anual(sig=sig)
        for row in res:
            print(f" {row['anio']}: Ene {row['p_inicial_real']:.2f}->{row['p_inicial_aprox']:.2f} "
                  f"Dic {row['p_final_real']:.2f}->{row['p_final_aprox']:.2f} "
                  f"Delta real {row['delta_real']:+.2f} aprox {row['delta_aprox']:+.2f} "
                  f"+/- {row['ea_delta']:.2f} Er {row['er_delta_pct']:.1f}% "
                  f"{'CONCLUYENTE' if row['concluyente'] else 'NO CONCLUYENTE'}")
        # comun de años poco confiables
        poco = [r for r in res if not r["concluyente"] or r["er_delta_pct"] > 10]
        if poco:
            print(f"  Años poco confiables ({sig} sig): {[r['anio'] for r in poco]} "
                  "- tienen Delta pequeño frente a Ea (cancelacion)")

        # guardar csv
        path = out_dir / f"anualidad_{sig}sig.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["anio", "enero_real", "enero_aprox", "dici_real", "dici_aprox",
                        "delta_real", "delta_aprox", "ea_delta", "er_delta_pct", "concluyente"])
            for r in res:
                w.writerow([r["anio"], f"{r['p_inicial_real']:.2f}", f"{r['p_inicial_aprox']:.2f}",
                            f"{r['p_final_real']:.2f}", f"{r['p_final_aprox']:.2f}",
                            f"{r['delta_real']:.2f}", f"{r['delta_aprox']:.2f}",
                            f"{r['ea_delta']:.4f}", f"{r['er_delta_pct']:.2f}", r["concluyente"]])
        print(f"Tabla escrita: {path}")


if __name__ == "__main__":
    main()
