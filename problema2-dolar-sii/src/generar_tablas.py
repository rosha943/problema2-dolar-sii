import pathlib
import csv
import numpy as np
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cargar_datos import cargar_datos, extraer_series
from errores import redondear_sig, error_absoluto, error_relativo, evaluar_compra_venta, evaluar_delta

OUT = pathlib.Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)

data = cargar_datos()
_, _, _, valores, etiquetas = extraer_series(data)

# 1. delta mes a mes 2 sig y 3 sig
for SIG in [2, 3]:
    aprox = redondear_sig(valores, sig=SIG)
    ea = error_absoluto(valores, aprox)
    path = OUT / f"delta_mes_a_mes_{SIG}sig.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["desde", "hasta", "delta_real", "delta_aprox", "ea_delta", "er_delta_pct", "concluyente", "signo_seguro"])
        for i in range(len(valores)-1):
            d = evaluar_delta(float(valores[i]), float(valores[i+1]), sig=SIG)
            w.writerow([etiquetas[i], etiquetas[i+1], f"{d['delta_real']:.2f}", f"{d['delta_aprox']:.2f}", f"{d['ea_delta']:.2f}", f"{d['er_delta_pct']:.1f}", d["concluyente"], d["signo_seguro"]])
    print(f"Escrito {path}")

# 2. rentabilidad desde minimo
idx_min = int(np.argmin(valores))
p_min = float(valores[idx_min])
for SIG in [2, 3]:
    path = OUT / f"rentabilidad_desde_minimo_{SIG}sig.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["etiqueta_compra", "p_compra_real", "p_compra_aprox", "etiqueta_venta", "p_venta_real", "p_venta_aprox", "usd", "pesos_final", "ganancia", "ea_ganancia", "er_ganancia_pct", "rent_pct", "ea_rent", "solida"])
        for j in range(idx_min+1, len(valores)):
            r = evaluar_compra_venta(p_min, float(valores[j]), sig=SIG)
            w.writerow([etiquetas[idx_min], f"{r['p_compra_real']:.2f}", f"{r['p_compra_aprox']:.2f}", etiquetas[j], f"{r['p_venta_real']:.2f}", f"{r['p_venta_aprox']:.2f}", f"{r['usd']:.2f}", f"{r['pesos_final']:.2f}", f"{r['ganancia']:.2f}", f"{r['ea_ganancia']:.2f}", f"{r['er_ganancia']:.1f}", f"{r['rentabilidad_pct']:.2f}", f"{r['ea_rent']:.2f}", r['rentabilidad_pct']>r['ea_rent']])
    print(f"Escrito {path}")

# 3. ejemplos compra venta
path = OUT / "ejemplos_compra_venta.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sig", "compra_real", "venta_real", "compra_aprox", "venta_aprox", "ea_compra", "ea_venta", "er_compra", "er_venta", "usd", "pesos_final", "ganancia", "ea_ganancia", "er_ganancia_pct", "rent_pct", "descripcion"])
    ejemplos = [
        (798.26, 1000.76, "min(Feb23)->max(Ene25)"),
        (875.66, 874.67, "dic22->dic23 cancelacion"),
        (822.05, 875.66, "2022 ene->dic"),
        (826.34, 874.67, "2023 ene->dic"),
        (907.99, 982.30, "2024 ene->dic"),
        (1000.76, 916.16, "2025 ene->dic"),
        (799.19, 953.71, "2022 mar->jul subida grande"),
    ]
    for sig in [2, 3]:
        for compra, venta, desc in ejemplos:
            r = evaluar_compra_venta(compra, venta, sig=sig)
            w.writerow([sig, compra, venta, r['p_compra_aprox'], r['p_venta_aprox'], f"{r['ea_compra']:.2f}", f"{r['ea_venta']:.2f}", f"{r['er_compra']:.3f}", f"{r['er_venta']:.3f}", f"{r['usd']:.2f}", f"{r['pesos_final']:.2f}", f"{r['ganancia']:.2f}", f"{r['ea_ganancia']:.2f}", f"{r['er_ganancia']:.1f}", f"{r['rentabilidad_pct']:.2f}", desc])
print(f"Escrito {path}")

# 4. A3 detallado
path = OUT / "A3_cancelacion_diciembre.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sig", "p_inicial_real", "p_final_real", "p_inicial_aprox", "p_final_aprox", "delta_real", "delta_aprox", "ea_delta", "er_delta_pct", "concluyente"])
    for sig in [2, 3]:
        d = evaluar_delta(875.66, 874.67, sig=sig)
        w.writerow([sig, d['p_inicial_real'], d['p_final_real'], d['p_inicial_aprox'], d['p_final_aprox'], d['delta_real'], d['delta_aprox'], d['ea_delta'], f"{d['er_delta_pct']:.1f}", d['concluyente']])
print(f"Escrito {path}")

# 5. B4 detalle
path = OUT / "B4_float_comparacion.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tipo", "valor"])
    a = 874.67
    b = 875.66
    verdadero = a - b
    f32 = float(np.float32(a) - np.float32(b))
    f64 = float(np.float64(a) - np.float64(b))
    w.writerow(["verdadero", verdadero])
    w.writerow(["float32", f32])
    w.writerow(["float64", f64])
    w.writerow(["ea_float32", abs(f32 - verdadero)])
    w.writerow(["ea_float64", abs(f64 - verdadero)])
print(f"Escrito {path}")

print("Tablas adicionales generadas.")
