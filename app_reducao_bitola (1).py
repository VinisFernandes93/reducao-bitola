import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Calculadora de Redução de Bitola (até 13 passes)", layout="centered")
st.title("Calculadora de Redução de Bitola — até 13 passes")

st.markdown(
    """
    Informe as reduções **percentuais por passe** (até 13) e, opcionalmente, o valor inicial de **diâmetro (mm)** ou **área (mm²)**.
    O aplicativo calcula a **redução acumulada**, o **valor final** e mostra a **evolução por passe**.
    Agora também exibe a **redução individual por passe (%)** e verifica se você está em **reduções decrescentes**.
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
reducoes_pct = []  # em porcentagem informada pelo usuário
reducoes_frac = [] # em fração (0-1)
for i in range(1, int(num_passes) + 1):
    r_pct = st.number_input(f"Passe {i}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.3f")
    reducoes_pct.append(r_pct)
    reducoes_frac.append(r_pct / 100.0)

# Checagem de reduções decrescentes (r1 >= r2 >= ...)
if len(reducoes_pct) > 1:
    decrescente = all(reducoes_pct[i] >= reducoes_pct[i+1] for i in range(len(reducoes_pct)-1))
else:
    decrescente = True

if decrescente:
    st.success("Sequência de reduções: **decrescente** (r₁ ≥ r₂ ≥ r₃ …)")
else:
    st.warning("Sequência de reduções: **não decrescente**. Existem passes com redução maior que o anterior.")

# Cálculo do fator acumulado: produto de (1 - r)
fator_restante = 1.0
for r in reducoes_frac:
    fator_restante *= (1.0 - r)

reducao_total_pct = (1.0 - fator_restante) * 100.0

# Apresentação dos resultados principais
st.markdown("### Resultado acumulado")
st.metric("Redução total (%)", f"{reducao_total_pct:.3f}%")
st.metric("Fator restante", f"{fator_restante:.6f}")

valor_final = None

# Construção de tabela por passe, sempre mostrando redução do passe (%)
linhas = []
fator_acum = 1.0
valor_atual = valor_inicial if (valor_inicial and valor_inicial > 0) else None

# Linha inicial, se houver valor
if valor_atual is not None:
    linhas.append({
        "Passe": "Inicial",
        "Redução do passe (%)": None,
        "Fator restante": fator_acum,
        ("Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)"): valor_atual
    })

for idx, r_frac in enumerate(reducoes_frac, start=1):
    fator = (1.0 - r_frac)
    fator_acum *= fator
    if valor_atual is not None:
        valor_atual = valor_atual * fator
    linhas.append({
        "Passe": idx,
        "Redução do passe (%)": reducoes_pct[idx-1],
        "Fator restante": fator_acum,
        ("Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)"): valor_atual
    })

# Exibir tabela
cols_base = ["Passe", "Redução do passe (%)", "Fator restante"]
valor_col = ("Diâmetro (mm)" if grandeza == "Diâmetro (mm)" else "Área (mm²)")

if valor_atual is not None:
    df = pd.DataFrame(linhas)
    st.markdown("### Evolução por passe (com redução individual)")
    st.dataframe(df, use_container_width=True)

    # Gráfico da evolução
    st.line_chart(df.set_index("Passe")[valor_col], height=300)

    valor_final = valor_atual
    st.markdown("---")
    st.success(f"Valor final ({valor_col}): {valor_final:.6f}")
else:
    # Se não houver valor inicial, ainda mostramos as reduções por passe e fator acumulado
    df = pd.DataFrame([{k: v for k, v in row.items() if k in cols_base} for row in linhas])
    st.markdown("### Passes e fatores (sem valor inicial)")
    st.dataframe(df, use_container_width=True)

# Conversões para fio redondo
if valor_atual is not None and eh_redondo:
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
csv = pd.DataFrame(linhas).to_csv(index=False).encode("utf-8")
st.download_button(
    label="Baixar tabela em CSV",
    data=csv,
    file_name="evolucao_reducao_bitola.csv",
    mime="text/csv",
)

st.caption(
    """
    Notas:
    • A redução por passe é aplicada sequencialmente como fator (1 - redução%).
    • A redução acumulada não é a soma simples das reduções individuais.
    • Para fio redondo, considera-se área = π·d²/4.
    • Agora você vê cada **Redução do passe (%)** para verificar se está em sequência decrescente.
    """
)
