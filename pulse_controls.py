def update_pulse(config, value, label):
    """
    Atualiza o valor da largura de pulso.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a largura de pulso.
        label: Widget de label para exibir o valor atualizado.
    """
    config.pulse_width = float(value)
    label.config(text=f"{float(value):.2f}")