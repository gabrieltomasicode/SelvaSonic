def update_additive(config, value, label):
    """
    Atualiza o número de harmônicos para síntese aditiva.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo número de harmônicos.
        label: Widget de label para exibir o valor atualizado.
    """
    config.additive_harmonics = int(float(value))
    label.config(text=str(int(float(value))))