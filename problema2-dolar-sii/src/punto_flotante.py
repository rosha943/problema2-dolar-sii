"""
punto_flotante.py - B1, B2, B4.

B1: Cifras significativas = mantisa corta. Demuestra error de representacion.
B2: Ida y vuelta M -> USD -> M con mismo precio, mide deriva en float32/float64 y grafica.
B4: Cancelacion en la maquina: 874.67 - 875.66 en float32 vs float64.
"""
import numpy as np
import pathlib

try:
    from src.cargar_datos import cargar_datos, extraer_series
    from src.errores import redondear_sig
except ImportError:
    from cargar_datos import cargar_datos, extraer_series
    from errores import redondear_sig


def demostrar_B1():
    """
    B1: Por que 2 cifras ~ mantisa corta.
    Ejemplo 1000.76 con 3 cifras.
    """
    print("=== B1: Cifras significativas = mantisa corta ===")
    print("Guardar con 2 sig en base 10 equivale a una mantisa de pocos digitos decimales,")
    print("analogo a pocos bits en binario: se pierde informacion de los digitos menos significativos.")
    print("Ejemplos:")
    for v in [963.44, 1000.76, 822.05]:
        for sig in [2, 3]:
            aprox = float(redondear_sig(v, sig=sig))
            ea = abs(v - aprox)
            er = ea / abs(v) * 100
            print(f"  {v} con {sig} sig -> {aprox} Ea {ea:.4f} Er {er:.4f}%")
    # caso pedido: 1000.76 con 3 cifras
    v = 1000.76
    aprox3 = float(redondear_sig(v, sig=3))
    print(f"\nPedido: 1000.76 con 3 cifras -> {aprox3} (1000) Ea {abs(v-aprox3):.2f} Er {abs(v-aprox3)/v*100:.3f}%")
    print("En binario, float32 tiene 24 bits de mantisa (~7 digitos decimales), float64 53 bits (~15-16).")
    print("Reducir a 2 sig decimales es aun mas agresivo: solo 2 digitos utiles, como una mantisa de ~7 bits decimales.")


def calcular_deriva_ida_vuelta(monto=1_000_000):
    """
    B2: Compra y vende al mismo precio, deberia volver a monto exacto.
    Retorna dict con derivas por mes para float32 y float64.
    """
    data = cargar_datos()
    _, _, _, valores, etiquetas = extraer_series(data)
    derivas_f32 = []
    derivas_f64 = []
    for v in valores:
        for dtype, lista in [(np.float32, derivas_f32), (np.float64, derivas_f64)]:
            m = dtype(monto)
            p = dtype(v)
            usd = m / p
            back = usd * p
            diff = float(back - m)
            lista.append(diff)
    return etiquetas, valores, np.array(derivas_f32), np.array(derivas_f64)


def demostrar_B2(graficar=True):
    print("\n=== B2: Ida y vuelta que no vuelve ===")
    etiquetas, valores, d_f32, d_f64 = calcular_deriva_ida_vuelta()
    print(f"Deriva max float32: {np.max(np.abs(d_f32)):.6f} CLP")
    print(f"Deriva max float64: {np.max(np.abs(d_f64)):.10f} CLP")
    print(f"Ejemplo 807.07 float32 deriva {d_f32[1]:.6f}, float64 {d_f64[1]:.10f}")
    # muestra si deriva sigue patron de curva: correlacion con valor
    corr_f32 = np.corrcoef(valores, np.abs(d_f32))[0, 1]
    print(f"Correlacion |deriva| vs precio (f32): {corr_f32:.3f} (no sigue patron claro, es ruido de redondeo binario)")

    if graficar:
        try:
            import matplotlib.pyplot as plt
            out = pathlib.Path(__file__).resolve().parents[1] / "graficos" / "05_deriva_ida_vuelta.png"
            out.parent.mkdir(exist_ok=True)
            fig, ax = plt.subplots(figsize=(12, 4))
            x = np.arange(len(etiquetas))
            ax.plot(x, d_f32, marker="o", ms=3, label="float32 deriva (CLP)")
            ax.plot(x, d_f64, marker="s", ms=3, label="float64 deriva (CLP)")
            ax.axhline(0, color="k", lw=0.8)
            ax.set_xticks(x[::4])
            ax.set_xticklabels(etiquetas[::4], rotation=45, ha="right")
            ax.set_ylabel("Deriva (pesos recuperados - M)")
            ax.set_title("B2: Deriva de la ida y vuelta M -> USD -> M (mismo precio)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(out, dpi=150)
            plt.close(fig)
            print(f"Grafico guardado: {out}")
        except Exception as e:
            print(f"No se pudo graficar B2: {e}")
    return etiquetas, valores, d_f32, d_f64


def demostrar_B4():
    print("\n=== B4: Cancelacion en la maquina ===")
    a = 874.67
    b = 875.66
    verdadero = a - b  # -0.99
    f32 = float(np.float32(a) - np.float32(b))
    f64 = float(np.float64(a) - np.float64(b))
    ea_f32 = abs(f32 - verdadero)
    ea_f64 = abs(f64 - verdadero)
    # cifras significativas validas ~ -log10(Ea/|resultado|)
    def cifras_validas(ea, ref):
        if ea == 0 or ref == 0:
            return float("inf")
        return -math.log10(ea / abs(ref)) if ea != 0 else float("inf")
    import math
    cv_f32 = cifras_validas(ea_f32, verdadero)
    cv_f64 = cifras_validas(ea_f64, verdadero)
    print(f"  874.67 - 875.66 verdadero = {verdadero}")
    print(f"  float32 = {f32:.10f} Ea {ea_f32:.2e} cifras validas ~{cv_f32:.1f}")
    print(f"  float64 = {f64:.15f} Ea {ea_f64:.2e} cifras validas ~{cv_f64:.1f}")
    print(f"  float32 pierde ~{15 - cv_f32:.1f} cifras respecto a float64 por mantisa corta (24 vs 53 bits)")
    print(f"  Conexion A3: con 2 sig Ea~9.0 Er 910%, con float32 Ea~1e-05 Er 0.001% - la cancelacion por redondeo decimal es 6 ordenes peor que la binaria, pero ambas muestran perdida de significancia al restar numeros cercanos.")
    return {"f32": f32, "f64": f64, "ea_f32": ea_f32, "ea_f64": ea_f64, "cv_f32": cv_f32, "cv_f64": cv_f64}


def main():
    demostrar_B1()
    demostrar_B2(graficar=True)
    demostrar_B4()


if __name__ == "__main__":
    main()
