from synth.utils import validate_adsr

def update_adsr(config, param, value, label):
    """
    Atualiza os parâmetros do envelope ADSR.

    Args:
        config: Instância de configuração do sintetizador.
        param: Nome do parâmetro ('Attack', 'Decay', 'Sustain', 'Release').
        value: Novo valor para o parâmetro.
        label: Widget de label para exibir o valor atualizado.
    """
    value = validate_adsr(param, value)
    label.config(text=f"{value:.2f}")

    if param == 'Sustain':
        config.sustain_level = value
    else:
        setattr(config, f"{param.lower()}_time", value)

def update_adsr_curve(config, curve_combo):
    """
    Atualiza o tipo de curva do envelope ADSR com base na seleção do usuário.

    Args:
        config: Instância de configuração do sintetizador.
        curve_combo: Combobox do tipo de curva (Linear/Exponential).
    """
    value = curve_combo.get().lower()
    if value == "linear":
        config.adsr_curve = config.ADSRCurve.LINEAR
    elif value == "exponential":
        config.adsr_curve = config.ADSRCurve.EXPONENTIAL