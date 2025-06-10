def update_polyphony(config, value, label):
    """
    Atualiza o número máximo de vozes simultâneas.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo número máximo de vozes.
        label: Widget de label para exibir o valor atualizado.
    """
    max_polyphony = int(float(value))
    config.max_polyphony = max_polyphony
    label.config(text=str(max_polyphony))