def update_filter_type(config, value):
    """
    Atualiza o tipo de filtro do sintetizador.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo tipo de filtro selecionado.
    """
    config.filter_type = value

def update_filter_freq(config, value, label):
    """
    Atualiza a frequência de corte do filtro.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a frequência de corte.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.filter_freq = val
    label.config(text=f"{val:.0f}")

def update_filter_q(config, value, label):
    """
    Atualiza o valor de Q (ressonância) do filtro.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor de Q.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.filter_q = val
    label.config(text=f"{val:.2f}")