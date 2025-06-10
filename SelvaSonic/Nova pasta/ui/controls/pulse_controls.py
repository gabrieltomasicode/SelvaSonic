def update_pulse(config, value, label):
    """
    Atualiza o valor da largura de pulso.
    """
    config.pulse_width = float(value)
    label.config(text=f"{float(value):.2f}")