<<<<<<< HEAD
def update_filter_type(config, combobox):
    config.filter_type = combobox.get()

def update_filter_freq(config, value, label):
    val = float(value)
    config.filter_freq = val
    label.config(text=f"{val:.0f}")

def update_filter_q(config, value, label):
    val = float(value)
    config.filter_q = val
=======
def update_filter_type(config, combobox):
    config.filter_type = combobox.get()

def update_filter_freq(config, value, label):
    val = float(value)
    config.filter_freq = val
    label.config(text=f"{val:.0f}")

def update_filter_q(config, value, label):
    val = float(value)
    config.filter_q = val
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    label.config(text=f"{val:.2f}")