"""
generar_graficos.py - Genera las 5 graficas obligatorias (numpy + matplotlib).
1. Serie mensual del dolar observado 2022-2025 (linea).
2. Variacion mes a mes DeltaP (barras) con error.
3. Error de representacion por mes al usar 2 cifras (barras Ea/Er).
4. Rentabilidad de comprar en el minimo y vender en cada mes posterior con barras de error.
5. Deriva de la ida y vuelta en punto flotante (de B2, aqui también).
"""
import pathlib
import numpy as np
import matplotlib.pyplot as plt

try:
    from src.cargar_datos import cargar_datos, extraer_series
    from src.errores import redondear_sig, error_absoluto, error_relativo, evaluar_compra_venta, evaluar_delta
    from src.punto_flotante import calcular_deriva_ida_vuelta
except ImportError:
    from cargar_datos import cargar_datos, extraer_series
    from errores import redondear_sig, error_absoluto, error_relativo, evaluar_compra_venta, evaluar_delta
    from punto_flotante import calcular_deriva_ida_vuelta

SIG = 2  # norma base del laboratorio
OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "graficos"
OUT_DIR.mkdir(exist_ok=True)
plt.rcParams["figure.dpi"] = 150

def graf1_serie_mensual():
    data = cargar_datos()
    _, _, _, valores, etiquetas = extraer_series(data)
    anios = data["anio"]
    fig, ax = plt.subplots(figsize=(12, 4))
    x = np.arange(len(valores))
    ax.plot(x, valores, marker="o", ms=3, color="#1f77b4", lw=1.5)
    ax.set_xticks(x[::4])
    ax.set_xticklabels(etiquetas[::4], rotation=45, ha="right")
    ax.set_ylabel("CLP por USD")
    ax.set_title("Serie mensual del dolar observado SII 2022-2025")
    # anotar min y max
    idx_min = int(np.argmin(valores))
    idx_max = int(np.argmax(valores))
    ax.scatter([idx_min, idx_max], [valores[idx_min], valores[idx_max]], color="red", zorder=5)
    ax.annotate(f"Min {etiquetas[idx_min]} {valores[idx_min]:.2f}", xy=(idx_min, valores[idx_min]), xytext=(10, 15), textcoords="offset points", arrowprops=dict(arrowstyle="->", color="red"), fontsize=8, color="red")
    ax.annotate(f"Max {etiquetas[idx_max]} {valores[idx_max]:.2f}", xy=(idx_max, valores[idx_max]), xytext=(10, -15), textcoords="offset points", arrowprops=dict(arrowstyle="->", color="red"), fontsize=8, color="red")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = OUT_DIR / "01_serie_mensual.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Grafico 1: {path}")

def graf2_delta_mes_a_mes():
    data = cargar_datos()
    _, _, _, valores, etiquetas = extraer_series(data)
    aprox = redondear_sig(valores, sig=SIG)
    ea = error_absoluto(valores, aprox)
    # Delta mes a mes (48 valores -> 47 deltas)
    delta_real = np.diff(valores)
    delta_aprox = np.diff(aprox)
    ea_delta = ea[:-1] + ea[1:]  # suma absolutos
    er_delta = np.where(delta_aprox != 0, np.abs(ea_delta / delta_aprox * 100), np.inf)
    # etiquetas centradas entre meses
    x = np.arange(len(delta_real))
    colores = ["#d62728" if abs(dr) <= ea else "#2ca02c" for dr, ea in zip(delta_aprox, ea_delta)]
    fig, ax = plt.subplots(figsize=(12, 4))
    bars = ax.bar(x, delta_aprox, yerr=ea_delta, capsize=2, color=colores, edgecolor="k", lw=0.3, error_kw={"ecolor": "gray", "alpha": 0.8})
    ax.set_xticks(x[::4])
    ax.set_xticklabels([f"{etiquetas[i]}->{etiquetas[i+1]}" for i in x[::4]], rotation=45, ha="right", fontsize=7)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("DeltaP aprox (CLP) +/- Ea")
    ax.set_title(f"Variacion mes a mes DeltaP ({SIG} sig) - rojo: |Delta| <= Ea (cancelacion)")
    ax.grid(axis="y", alpha=0.3)
    # leyenda
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#d62728", label="No concluyente (|Delta|<=Ea)"), Patch(color="#2ca02c", label="Concluyente")], fontsize=8)
    fig.tight_layout()
    path = OUT_DIR / "02_delta_mes_a_mes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Grafico 2: {path}")
    # imprime casos no concluyentes
    print("  Tramos no concluyentes (|Delta|<=Ea):")
    for i in range(len(delta_aprox)):
        if abs(delta_aprox[i]) <= ea_delta[i]:
            print(f"    {etiquetas[i]}->{etiquetas[i+1]} delta_aprox {delta_aprox[i]:.2f} Ea {ea_delta[i]:.2f} Er {er_delta[i]:.1f}%")

def graf3_error_representacion():
    data = cargar_datos()
    _, _, _, valores, etiquetas = extraer_series(data)
    aprox = redondear_sig(valores, sig=SIG)
    ea = error_absoluto(valores, aprox)
    er = error_relativo(ea, valores)
    x = np.arange(len(valores))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    ax1.bar(x, ea, color="#ff7f0e", edgecolor="k", lw=0.3)
    ax1.set_ylabel("Ea (CLP)")
    ax1.set_title(f"Error de representacion por mes al usar {SIG} cifras (Ea)")
    ax1.grid(axis="y", alpha=0.3)
    ax2.bar(x, er, color="#9467bd", edgecolor="k", lw=0.3)
    ax2.set_ylabel("Er (%)")
    ax2.set_title(f"Error relativo por mes ({SIG} sig)")
    ax2.set_xticks(x[::4])
    ax2.set_xticklabels(etiquetas[::4], rotation=45, ha="right")
    ax2.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = OUT_DIR / "03_error_representacion.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Grafico 3: {path}")

def graf4_rentabilidad_desde_minimo():
    data = cargar_datos()
    _, _, _, valores, etiquetas = extraer_series(data)
    idx_min = int(np.argmin(valores))
    p_min_real = float(valores[idx_min])
    etiqueta_min = etiquetas[idx_min]
    # vender en cada mes posterior al minimo
    indices = np.arange(idx_min + 1, len(valores))
    rents = []
    eas = []
    ers = []
    etiquetas_post = []
    for j in indices:
        r = evaluar_compra_venta(p_min_real, float(valores[j]), sig=SIG)
        rents.append(r["rentabilidad_pct"])
        eas.append(r["ea_rent"])
        ers.append(r["er_rent"])
        etiquetas_post.append(etiquetas[j])
    rents = np.array(rents)
    eas = np.array(eas)
    fig, ax = plt.subplots(figsize=(12, 4))
    x = np.arange(len(rents))
    ax.bar(x, rents, yerr=eas, capsize=2, color="#17becf", edgecolor="k", lw=0.3, error_kw={"ecolor": "gray"})
    ax.set_xticks(x[::3] if len(x) > 12 else x)
    ax.set_xticklabels([etiquetas_post[i] for i in (np.arange(len(x))[::3] if len(x)>12 else np.arange(len(x)))], rotation=45, ha="right", fontsize=7)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Rentabilidad (%) +/- Ea")
    ax.set_title(f"Rentabilidad comprar en minimo ({etiqueta_min} {p_min_real:.2f} CLP) y vender en cada mes posterior ({SIG} sig)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = OUT_DIR / "04_rentabilidad_desde_minimo.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Grafico 4: {path}")
    # destacar si siempre solida
    solidas = rents > eas
    print(f"  Compras desde minimo: {np.sum(solidas)}/{len(rents)} son solidas (rent > Ea)")
    # mejor post-minimo
    idx_best = int(np.argmax(rents))
    print(f"  Mejor venta post-minimo: {etiquetas_post[idx_best]} rent {rents[idx_best]:.2f}% +/- {eas[idx_best]:.2f}")

def graf5_deriva():
    # Reuso B2 pero graficando directo
    etiquetas, valores, d_f32, d_f64 = calcular_deriva_ida_vuelta()
    fig, ax = plt.subplots(figsize=(12, 4))
    x = np.arange(len(valores))
    ax.plot(x, d_f32, marker="o", ms=3, label="float32", color="#d62728")
    ax.plot(x, d_f64, marker="s", ms=3, label="float64", color="#2ca02c")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x[::4])
    ax.set_xticklabels(etiquetas[::4], rotation=45, ha="right")
    ax.set_ylabel("Deriva (back - M) CLP")
    ax.set_title("Deriva ida y vuelta M -> USD -> M (B2)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = OUT_DIR / "05_deriva_ida_vuelta.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Grafico 5: {path}")

def main():
    graf1_serie_mensual()
    graf2_delta_mes_a_mes()
    graf3_error_representacion()
    graf4_rentabilidad_desde_minimo()
    graf5_deriva()
    print("Todos los graficos generados en", OUT_DIR)

if __name__ == "__main__":
    main()
