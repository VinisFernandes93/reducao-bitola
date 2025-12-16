# Calculadora de Redução de Bitola — até 13 passes

Aplicativo **Streamlit** para calcular a redução sequencial de bitola (diâmetro ou área) em até **13 passes**.

## ✨ Recursos
- Entrada de reduções por passe (1 a 13), com casas decimais.
- Grandeza principal: **Diâmetro (mm)** ou **Área (mm²)**.
- Valor inicial opcional e **evolução por passe** (tabela e gráfico).
- Conversão automática para **fio redondo**: área ↔ diâmetro.
- Download da tabela em **CSV**.

## 🚀 Como rodar localmente
```bash
pip install -r requirements.txt
streamlit run app_reducao_bitola.py
```

## ☁️ Deploy no Streamlit Community Cloud
1. Crie um repositório no **GitHub** com estes arquivos:
   - `app_reducao_bitola.py`
   - `requirements.txt`
   - `README.md`
2. Acesse **https://streamlit.io/cloud** e clique em **Deploy an app**.
3. Selecione o repositório e o arquivo **`app_reducao_bitola.py`**.
4. Aguarde o build e use o link gerado para compartilhar.

## 🔍 Fórmulas
Para reduções sequenciais `r_i` (em fração), o fator restante é:
```
F = ∏(1 - r_i)
Redução total (%) = (1 - F) × 100
Valor final = Valor inicial × F
```
Para fio redondo:
```
Área = π·d²/4
Diâmetro = √(4·Área/π)
```

## 📝 Licença
Uso livre para fins internos. Ajuste conforme sua necessidade.
