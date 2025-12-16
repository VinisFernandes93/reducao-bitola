
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
    decrescente = all(reducoes_pct[i] >= reducoes_pct[i+1] for i in range(len(reducoes_pct)-1))
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
valor_col = ("Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)")
valor_atual = valor_inicial if (valor_inicial and valor_inicial > 0) else None

# Linha inicial, se houver valor
if valor_atual is not None:
    linhas.append({
        "Passe": "Inicial",
        "Redução entre passes (%)": None,
        "Redução acumulada (%)": 0.0,
        "Fator restante": 1.0,
