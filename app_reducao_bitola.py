
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Calculadora de Redução de Bitola (até 13 passes)", layout="centered")
st.title("Calculadora de Redução de Bitola — até 13 passes")

st.markdown(
    """
    Informe as reduções **percentuais por passe** (até 13) e, opcionalmente, o valor inicial de **diâmetro (mm)** ou **área (mm²)**.
    O aplicativo calcula a **redução acumulada**, o **valor final** e mostra a **evolução por passe**.
    """
)

# Escolha da grandeza principal
col_a, col_b = st.columns(2)
with col_a:
    grandeza = st.selectbox("Grandeza principal", ["Diâmetro (mm)", "Área (mm²)"])
with col_b:
    eh_redondo = st.checkbox("Fio redondo (converter entre diâmetro e área)", value=True)

# Valor inicial (opcional)
if grandeza == "Diâmetro (mm)":
    valor_inicial = st.number_input("Diâmetro inicial (mm) — opcional", min_value=0.0, format="%.6f")
else:
    valor_inicial = st.number_input("Área inicial (mm²) — opcional", min_value=0.0, format="%.6f")

# Número de passes
num_passes = st.number_input("Quantos passes?", min_value=1, max_value=13, value=5)

st.markdown("### Reduções por passe (%)")
reducoes = []
for i in range(1, int(num_passes) + 1):
    r = st.number_input(f"Passe {i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.3f")
    reducoes.append(r / 100.0)

# Remover passes de redução zero do cálculo acumulado, mas manter na tabela se valor inicial existir
reducoes_validas = [r for r in reducoes if r > 0]

# Cálculo do fator acumulado: produto de (1 - r)
fator_restante = 1.0
for r in reducoes_validas:
    fator_restante *= (1.0 - r)

reducao_total_pct = (1.0 - fator_restante) * 100.0

# Apresentação dos resultados principais
st.markdown("### Resultado acumulado")
st.metric("Redução total (%)", f"{reducao_total_pct:.3f}%")
st.metric("Fator restante", f"{fator_restante:.6f}")

valor_final = None

# Se houver valor inicial, calcular evolução por passe
if valor_inicial and valor_inicial > 0:
    valores_por_passe = [valor_inicial]
    fatores_por_passe = [1.0]
    for r in reducoes:
        fator = (1.0 - r)
        novo_valor = valores_por_passe[-1] * fator
        valores_por_passe.append(novo_valor)
        fatores_por_passe.append(fatores_por_passe[-1] * fator)

    valor_final = valores_por_passe[-1]

    # Tabela de evolução
    import pandas as pd
    df = pd.DataFrame({
        "Passe": list(range(0, len(valores_por_passe))),
        "Fator restante": fatores_por_passe,
        ("Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)"): valores_por_passe
    })
    df.loc[0, "Passe"] = "Inicial"

    st.markdown("### Evolução por passe")
    st.dataframe(df, use_container_width=True)

    # Gráfico da evolução
    st.line_chart(df.set_index("Passe")[df.columns[-1]], height=300)

    # Conversões para fio redondo
    if eh_redondo:
        if grandeza == "Área (mm²)":
            # Converter áreas para diâmetros equivalentes
            import math
            diametros = [math.sqrt(4.0 * a / math.pi) for a in valores_por_passe]
            df_diam = pd.DataFrame({
                "Passe": df["Passe"],
                "Diâmetro (mm)": diametros
            })
            st.markdown("### Conversão para diâmetro (fio redondo)")
            st.dataframe(df_diam, use_container_width=True)
            st.line_chart(df_diam.set_index("Passe")["Diâmetro (mm)"], height=300)
        else:
            # Converter diâmetros para áreas equivalentes
            import math
            areas = [math.pi * (d ** 2) / 4.0 for d in valores_por_passe]
            df_area = pd.DataFrame({
                "Passe": df["Passe"],
                "Área (mm²)": areas
            })
            st.markdown("### Conversão para área (fio redondo)")
            st.dataframe(df_area, use_container_width=True)
            st.line_chart(df_area.set_index("Passe")["Área (mm²)"], height=300)

    # Download dos dados
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar tabela em CSV",
        data=csv,
        file_name="evolucao_reducao_bitola.csv",
        mime="text/csv",
    )

    st.markdown("---")
    unidade = "Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)"
    st.success(f"Valor final ({unidade}): {valor_final:.6f}")
else:
    st.info("Opcional: informe um valor inicial para ver a evolução por passe e o valor final.")

st.caption(
    "Notas:\n"
    "• A redução por passe é aplicada sequencialmente como fator (1 - redução%).\n"
    "• A redução acumulada não é a soma simples das reduções individuais.\n"
    "• Para fio redondo, considera-se área = π·d²/4."
)
