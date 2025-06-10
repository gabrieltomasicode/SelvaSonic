
def update_fm_freq(config, value, label):
    """
    Atualiza a frequência de modulação em frequência (FM).

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a frequência de modulação FM.
        label: Widget de label para exibir o valor atualizado.
    """
    config.fm_mod_freq = float(value)
    label.config(text=f"{float(value):.1f}")

def update_fm_index(config, value, label):
    """
    Atualiza o índice de modulação em frequência (FM).

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para o índice de modulação FM.
        label: Widget de label para exibir o valor atualizado.
    """
    config.fm_mod_index = float(value)
    label.config(text=f"{float(value):.2f}")

def update_lfo_freq(config, value, label):
    """
    Atualiza a frequência do LFO.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a frequência do LFO.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.lfo_freq = val
    label.config(text=f"{val:.2f} Hz")

def update_lfo_depth(config, value, label):
    """
    Atualiza a profundidade do LFO.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a profundidade do LFO.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.lfo_depth = val
    label.config(text=f"{val:.2f}")

def update_lfo_target(config, combobox):
    """
    Atualiza o alvo do LFO.

    Args:
        config: Instância de configuração do sintetizador.
        combobox: Combobox do alvo do LFO.
    """
    config.lfo_target = combobox.get()

def update_hfo_freq(config, value, label):
    """
    Atualiza a frequência do HFO.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a frequência do HFO.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.hfo_freq = val
    label.config(text=f"{val:.1f} Hz")

def update_hfo_depth(config, value, label):
    """
    Atualiza a profundidade do HFO.

    Args:
        config: Instância de configuração do sintetizador.
        value: Novo valor para a profundidade do HFO.
        label: Widget de label para exibir o valor atualizado.
    """
    val = float(value)
    config.hfo_depth = val
    label.config(text=f"{val:.2f}")

def update_hfo_target(config, combobox):
    """
    Atualiza o alvo do HFO.

    Args:
        config: Instância de configuração do sintetizador.
        combobox: Combobox do alvo do HFO.
    """
    config.hfo_target = combobox.get()