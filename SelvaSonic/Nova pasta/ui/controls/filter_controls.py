def update_filter_type(config, combobox):
    config.filter_type = combobox.get()

def update_filter_freq(config, value, label):
    val = float(value)
    config.filter_freq = val
    label.config(text=f"{val:.0f}")

def update_filter_q(config, value, label):
    val = float(value)
    config.filter_q = val
    label.config(text=f"{val:.2f}")