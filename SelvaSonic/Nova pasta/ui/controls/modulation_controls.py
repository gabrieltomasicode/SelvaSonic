
def update_fm_freq(config, value, label):
    """
    Atualiza a frequência de modulação em frequência (FM).
    """
    config.fm_mod_freq = float(value)
    label.config(text=f"{float(value):.1f}")

def update_fm_index(config, value, label):
    """
    Atualiza o índice de modulação em frequência (FM).
    """
    config.fm_mod_index = float(value)
    label.config(text=f"{float(value):.2f}")

def update_lfo_freq(config, value, label):
    val = float(value)
    config.lfo_freq = val
    label.config(text=f"{val:.2f} Hz")

def update_lfo_depth(config, value, label):
    val = float(value)
    config.lfo_depth = val
    label.config(text=f"{val:.2f}")

def update_lfo_target(config, combobox):
    config.lfo_target = combobox.get()

def update_hfo_freq(config, value, label):
    val = float(value)
    config.hfo_freq = val
    label.config(text=f"{val:.1f} Hz")

def update_hfo_depth(config, value, label):
    val = float(value)
    config.hfo_depth = val
    label.config(text=f"{val:.2f}")

def update_hfo_target(config, combobox):
    config.hfo_target = combobox.get()