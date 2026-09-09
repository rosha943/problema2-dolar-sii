"""
errores.py - Error absoluto, relativo y propagado entre puntos.
Implementa redondeo a N cifras significativas (vectorizado con numpy) y
las operaciones del laboratorio: compra/venta, ganancia, rentabilidad, DeltaP.

Normas del PDF (secs 4-6):
- Parametro base: 2 cifras significativas totales (mantisa corta), base 10.
  Ejemplo: 963.44 -> 960, 1000.76 -> 1000.
- Para A3 el enunciado pide 3 cifras (se incluye comparación 2 vs 3).
- Propagacion: multiplicacion/division -> se suman errores relativos.
               suma/resta -> se suman errores absolutos.
- Ea = |real - aprox|, Er = Ea/|real|*100
"""
import math
import numpy as np
from cargar_datos import cargar_datos, extraer_series

# Para import como modulo y como script
try:
    from src.cargar_datos import cargar_datos, extraer_series
except ImportError:
    from cargar_datos import cargar_datos, extraer_series


def redondear_sig(x, sig=2):
    """
    Redondea a `sig` cifras significativas (base 10).
    Vectorizado: acepta escalar o np.ndarray.
    Usa round() half-even de Python (coherente con ejemplo 963.44->960).
    """
    x_arr = np.asarray(x, dtype=float)
    escalar = x_arr.ndim == 0
    x_flat = x_arr.ravel()
    out = np.empty_like(x_flat, dtype=float)
    for i, v in enumerate(x_flat):
        if v == 0 or not np.isfinite(v):
            out[i] = 0.0 if v == 0 else v
        else:
            mag = math.floor(math.log10(abs(v)))
            factor = 10 ** (mag - sig + 1)
            out[i] = round(v / factor) * factor
    out = out.reshape(x_arr.shape)
    return float(out) if escalar else out


def error_absoluto(real, aprox):
    return np.abs(np.asarray(real, dtype=float) - np.asarray(aprox, dtype=float))


def error_relativo(ea, real):
    real = np.asarray(real, dtype=float)
    ea = np.asarray(ea, dtype=float)
    # evita division por cero
    with np.errstate(divide="ignore", invalid="ignore"):
        er = np.where(real != 0, ea / np.abs(real) * 100.0, np.inf)
    return er


def propagar_mult_div(er1, er2):
    """Suma de errores relativos para * y / ."""
    return np.asarray(er1) + np.asarray(er2)


def propagar_suma_resta(ea1, ea2):
    """Suma de errores absolutos para + y - ."""
    return np.asarray(ea1) + np.asarray(ea2)


# ---------- A1 ----------
def analisis_A1(sig=2, ruta_csv=None):
    """
    A1. Error de representación mes a mes.
    Retorna dict con vectores y el índice del mayor Er.
    """
    data = cargar_datos(ruta_csv)
    _, _, _, valores, etiquetas = extraer_series(data)
    aprox = redondear_sig(valores, sig=sig)
    ea = error_absoluto(valores, aprox)
    er = error_relativo(ea, valores)
    idx_max = int(np.argmax(er))
    return {
        "data": data,
        "valores": valores,
        "etiquetas": etiquetas,
        "aprox": aprox,
        "ea": ea,
        "er": er,
        "idx_max": idx_max,
    }


# ---------- A2, A5, Delta generico ----------
def evaluar_compra_venta(p_compra_real, p_venta_real, monto=1_000_000, sig=2):
    """
    A2/A5: compra M/Pcompra -> venta USD*Pventa -> ganancia.
    Propagacion: relativos se suman en / y *, luego se pasa a absoluto.
    Retorna dict con todos los pasos.
    """
    p_compra_aprox = float(redondear_sig(p_compra_real, sig=sig))
    p_venta_aprox = float(redondear_sig(p_venta_real, sig=sig))
    ea_compra = abs(p_compra_real - p_compra_aprox)
    ea_venta = abs(p_venta_real - p_venta_aprox)
    er_compra = ea_compra / abs(p_compra_real) * 100 if p_compra_real != 0 else 0
    er_venta = ea_venta / abs(p_venta_real) * 100 if p_venta_real != 0 else 0

    usd = monto / p_compra_aprox
    er_usd = er_compra  # division propaga er del divisor
    ea_usd = usd * er_usd / 100 if er_usd != 0 else 0

    pesos_final = usd * p_venta_aprox
    er_pesos = propagar_mult_div(er_usd, er_venta)  # suma relativos
    ea_pesos = pesos_final * er_pesos / 100

    ganancia = pesos_final - monto
    # resta: se suman absolutos. Monto es exacto (sin error), asi que ea_g = ea_pesos
    ea_ganancia = float(ea_pesos)
    er_ganancia = abs(ea_ganancia / ganancia * 100) if ganancia != 0 else float("inf")
    rentabilidad = ganancia / monto * 100
    er_rent = er_ganancia  # misma proporcion
    ea_rent = abs(rentabilidad * er_rent / 100) if np.isfinite(er_rent) else float("inf")

    return {
        "sig": sig,
        "p_compra_real": p_compra_real,
        "p_venta_real": p_venta_real,
        "p_compra_aprox": p_compra_aprox,
        "p_venta_aprox": p_venta_aprox,
        "ea_compra": ea_compra,
        "ea_venta": ea_venta,
        "er_compra": er_compra,
        "er_venta": er_venta,
        "usd": usd,
        "er_usd": er_usd,
        "ea_usd": ea_usd,
        "pesos_final": pesos_final,
        "er_pesos": float(er_pesos),
        "ea_pesos": float(ea_pesos),
        "ganancia": ganancia,
        "ea_ganancia": ea_ganancia,
        "er_ganancia": er_ganancia,
        "rentabilidad_pct": rentabilidad,
        "ea_rent": ea_rent,
        "er_rent": er_rent,
    }


def evaluar_delta(p_inicial_real, p_final_real, sig=2):
    """
    Evalua DeltaP = P_final - P_inicial con propagacion de resta.
    """
    p_ini_aprox = float(redondear_sig(p_inicial_real, sig=sig))
    p_fin_aprox = float(redondear_sig(p_final_real, sig=sig))
    ea_ini = abs(p_inicial_real - p_ini_aprox)
    ea_fin = abs(p_final_real - p_fin_aprox)
    delta_real = p_final_real - p_inicial_real
    delta_aprox = p_fin_aprox - p_ini_aprox
    ea_delta = ea_ini + ea_fin
    er_delta = abs(ea_delta / delta_aprox * 100) if delta_aprox != 0 else float("inf")
    er_delta_vs_real = abs(ea_delta / delta_real * 100) if delta_real != 0 else float("inf")
    # Norma arbitraria: no concluyente si |Delta| <= Ea
    concluyente = abs(delta_aprox) > ea_delta
    signo_seguro = (abs(delta_aprox) - ea_delta) > 0 and np.sign(delta_aprox) == np.sign(delta_real)
    return {
        "sig": sig,
        "p_inicial_real": p_inicial_real,
        "p_final_real": p_final_real,
        "p_inicial_aprox": p_ini_aprox,
        "p_final_aprox": p_fin_aprox,
        "ea_inicial": ea_ini,
        "ea_final": ea_fin,
        "delta_real": delta_real,
        "delta_aprox": delta_aprox,
        "ea_delta": ea_delta,
        "er_delta_pct": er_delta,
        "er_vs_real_pct": er_delta_vs_real,
        "concluyente": concluyente,
        "signo_seguro": signo_seguro,
    }


def main():
    import pathlib
    import csv

    print("=== A1: Error de representacion mes a mes (2 cifras) ===")
    for sig in [2, 3]:
        res = analisis_A1(sig=sig)
        idx = res["idx_max"]
        print(f"\n-- {sig} cifras: mayor Er -> {res['etiquetas'][idx]} "
              f"real {res['valores'][idx]:.2f} aprox {res['aprox'][idx]:.2f} "
              f"Ea {res['ea'][idx]:.2f} Er {res['er'][idx]:.4f}%")
        # ranking top 3
        order = np.argsort(res["er"])[::-1][:3]
        for j in order:
            print(f"  {res['etiquetas'][j]} {res['valores'][j]:.2f}->{res['aprox'][j]:.2f} Er {res['er'][j]:.3f}%")

    print("\n=== A2: Ejemplo compra-venta (elige dos meses) ===")
    # Ejemplo: comprar en mes barato Feb 2023 (798.26) vender en caro Ene 2025 (1000.76)
    for sig in [2, 3]:
        r = evaluar_compra_venta(798.26, 1000.76, sig=sig)
        print(f"\n sig {sig}: Compra {r['p_compra_real']}->{r['p_compra_aprox']} "
              f"Venta {r['p_venta_real']}->{r['p_venta_aprox']}")
        print(f"  USD {r['usd']:.2f} +/- {r['ea_usd']:.4f} (Er {r['er_usd']:.3f}%)")
        print(f"  Pesos final {r['pesos_final']:.2f} +/- {r['ea_pesos']:.2f} (Er {r['er_pesos']:.3f}%)")
        print(f"  Ganancia {r['ganancia']:.2f} +/- {r['ea_ganancia']:.2f} (Er {r['er_ganancia']:.1f}%) "
              f"Rent {r['rentabilidad_pct']:.2f}% +/- {r['ea_rent']:.2f}")

    print("\n=== A3: Cancelacion dic 2022 vs dic 2023 ===")
    for sig in [2, 3]:
        d = evaluar_delta(875.66, 874.67, sig=sig)
        print(f" sig {sig}: Delta real {d['delta_real']:.2f} aprox {d['delta_aprox']:.2f} "
              f"+/- {d['ea_delta']:.2f} Er {d['er_delta_pct']:.1f}% "
              f"Concluyente? {d['concluyente']}")

    print("\n=== A5: Mejor compra (min) y mejor venta (max) ===")
    data = cargar_datos()
    _, _, _, valores, _ = extraer_series(data)
    idx_min = int(np.argmin(valores))
    idx_max = int(np.argmax(valores))
    print(f" Min {data[idx_min]['anio']}-{data[idx_min]['mes']} {valores[idx_min]} "
          f"Max {data[idx_max]['anio']}-{data[idx_max]['mes']} {valores[idx_max]}")
    for sig in [2, 3]:
        r = evaluar_compra_venta(float(valores[idx_min]), float(valores[idx_max]), sig=sig)
        print(f"  sig {sig}: Rent {r['rentabilidad_pct']:.2f}% +/- {r['ea_rent']:.2f} "
              f"Er {r['er_rent']:.1f}% - {'SOLIDO' if r['rentabilidad_pct'] > r['ea_rent'] else 'EN DUDA'}")

    # Guardar tablas
    out_dir = pathlib.Path(__file__).resolve().parents[1] / "outputs"
    out_dir.mkdir(exist_ok=True)
    for sig in [2, 3]:
        res = analisis_A1(sig=sig)
        path = out_dir / f"errores_mensuales_{sig}sig.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["anio", "mes", "mes_num", "etiqueta", "valor_real", "valor_aprox", "ea", "er_pct"])
            for i, row in enumerate(res["data"]):
                w.writerow([row["anio"], row["mes"], row["mes_num"], res["etiquetas"][i],
                            f"{res['valores'][i]:.2f}", f"{res['aprox'][i]:.2f}",
                            f"{res['ea'][i]:.4f}", f"{res['er'][i]:.4f}"])
        print(f"Tabla escrita: {path}")


if __name__ == "__main__":
    main()
