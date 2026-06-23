def update_ss_voices(config, value, label):
    """
    Atualiza o número de vozes para o oscilador Super Saw.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo número de vozes para o Super Saw.
        label: Widget de label para exibir o valor atualizado.
    """
    config.super_saw_voices = int(round(float(value)))
    if label is not None:
        label.config(text=str(int(round(float(value)))))