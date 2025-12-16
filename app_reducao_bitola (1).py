
import math
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Calculadora de Redução de Bitola (até 13 passes)", layout="centered")
st.title("Calculadora de Redução de Bitola — até 13 passes")

st.markdown(
    """
    Informe as reduções **percentuais por passe** (até 13) e, opcionalmente, o valor inicial de **diâmetro (mm)** ou **área (mm²)**.
    O aplicativo calcula a **redução acumulada**, o **valor final** e mostra a **evolução por passe**.
    Também exibe explicitamente a **redução entre passes (%)** e a **redução acumulada por passe (%)**.
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

# Entradas de redução por passe
st.markdown("### Reduções por passe (%)")
reducoes_pct = []   # em porcentagem informada pelo usuário (ex.: 30, 28...)
reducoes_frac = []  # em fração (0–1) correspondente (ex.: 0.30, 0.28...)
for i in range(1, int(num_passes) + 1):
    r_pct = st.number_input(f"Passe {i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.3f")
    reducoes_pct.append(r_pct)
    reducoes_frac.append(r_pct / 100.0)

# Checagem de reduções decrescentes (r1 >= r2 >= r3 ...)
if len(reducoes_pct) > 1:
    decrescente = all(reducoes_pct[i] >= reducoes_pct[i + 1] for i in range(len(reducoes_pct) - 1))
else:
    decrescente = True

if decrescente:
    st.success("Sequência de reduções: **decrescente** (r₁ ≥ r₂ ≥ r₃ …)")
else:
    st.warning("Sequência de reduções: **não decrescente**. Existem passes com redução maior que o anterior.")

# Fator acumulado total e redução total
fator_restante_total = 1.0
fatores_acum = []  # fator restante após cada passe
for r in reducoes_frac:
    fator_restante_total *= (1.0 - r)
    fatores_acum.append(fator_restante_total)

reducao_total_pct = (1.0 - fator_restante_total) * 100.0

# Resultados principais
st.markdown("### Resultado acumulado")
st.metric("Redução total (%)", f"{reducao_total_pct:.3f}%")
st.metric("Fator restante", f"{fator_restante_total:.6f}")

# Construção da tabela por passe
linhas = []
valor_col = "Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)"
valor_atual = valor_inicial if (valor_inicial and valor_inicial > 0) else None

# Linha inicial, se houver valor
if valor_atual is not None:
    linhas.append({
        "Passe": "Inicial",
        "Redução entre passes (%)": None,
        "Redução acumulada (%)": 0.0,
        "Fator restante": 1.0,
        valor_col: valor_atual
    })

# Iteração dos passes
fator_acum = 1.0
for idx, r_frac in enumerate(reducoes_frac, start=1):
    # Fator do passe
    fator = (1.0 - r_frac)
    # Atualiza fator acumulado
    fator_acum *= fator

    # Valor após o passe (se houver valor inicial)
    if valor_atual is not None:
        valor_atual = valor_atual * fator

    # Redução entre passes (%) é exatamente o valor informado
    reducao_entre_pct = reducoes_pct[idx - 1]

    # Redução acumulada (%) até este passe
    reducao_acum_pct = (1.0 - fator_acum) * 100.0

    linha = {
        "Passe": idx,
        "Redução entre passes (%)": reducao_entre_pct,
        "Redução acumulada (%)": reducao_acum_pct,
        "Fator restante": fator_acum,
        valor_col: valor_atual
    }
    linhas.append(linha)

# DataFrame principal
df = pd.DataFrame(linhas)

# Exibir tabela principal
st.markdown("### Evolução por passe (inclui redução entre passes e acumulada)")
st.dataframe(df, use_container_width=True)

# Gráfico da grandeza principal (se houver valor inicial)
if valor_inicial and valor_inicial > 0:
    st.line_chart(df.set_index("Passe")[valor_col], height=300)
    st.markdown("---")
    st.success(f"Valor final ({valor_col}): {valor_atual:.6f}")

# Gráfico da redução entre passes (%)
if len(df) > 0:
    df_plot_red = df.dropna(subset=["Redução entre passes (%)"]).set_index("Passe")["Redução entre passes (%)"]
    st.markdown("### Gráfico — Redução entre passes (%)")
    st.bar_chart(df_plot_red, height=260)

# Conversões para fio redondo (se houver valor inicial)
if valor_inicial and valor_inicial > 0 and eh_redondo:
    if grandeza == "Área (mm²)":
        # Converter áreas para diâmetros equivalentes
        valores_area = [lin[valor_col] for lin in linhas if isinstance(lin[valor_col], (int, float))]
        diametros = [math.sqrt(4.0 * a / math.pi) for a in valores_area]
        df_diam = pd.DataFrame({
            "Passe": [lin["Passe"] for lin in linhas if isinstance(lin[valor_col], (int, float))],
            "Diâmetro (mm)": diametros
        })
        st.markdown("### Conversão para diâmetro (fio redondo)")
        st.dataframe(df_diam, use_container_width=True)
        st.line_chart(df_diam.set_index("Passe")["Diâmetro (mm)"], height=300)
    else:
        # Converter diâmetros para áreas equivalentes
        valores_diam = [lin[valor_col] for lin in linhas if isinstance(lin[valor_col], (int, float))]
        areas = [math.pi * (d ** 2) / 4.0 for d in valores_diam]
        df_area = pd.DataFrame({
            "Passe": [lin["Passe"] for lin in linhas if isinstance(lin[valor_col], (int, float))],
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

# Notas finais
st.caption(
    """
    Notas:
    • **Redução entre passes (%)** é o valor informado por passe (ex.: 30%, 28%, ...).
    • **Redução acumulada (%)** considera a sequência de fatores: F = ∏(1 - rᵢ).
      Até o passe k: Redução acumulada (%) = (1 - ∏_{i=1..k}(1 - rᵢ)) × 100.

