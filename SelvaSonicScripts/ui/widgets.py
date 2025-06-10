import tkinter as tk
from tkinter import ttk
from synth.config import SynthConfig, WaveType


def create_oscillator_controls(parent, config, on_waveform_change, on_pulse, on_ss_voices):
    
    """
    Cria e retorna os controles de oscilador para a interface gráfica.

    Esta função monta o painel de seleção de forma de onda, ajuste de pulse width e quantidade de vozes Super Saw.

    Parâmetros:
        parent: Widget pai onde os controles serão inseridos.
        config: Objeto de configuração do sintetizador.
        on_waveform_change: Callback para mudança de forma de onda.
        on_pulse: Callback para ajuste de pulse width.
        on_ss_voices: Callback para ajuste de vozes Super Saw.

    Retorna:
        dict: Dicionário com referências aos widgets criados.
    """

    frame = ttk.LabelFrame(parent, text="Oscilador")

    # Waveform Selection
    ttk.Label(frame, text="Waveform:").grid(row=0, column=0, padx=5, pady=5)
    waveform_combo = ttk.Combobox(frame, values=[w.value for w in WaveType], state="readonly")
    waveform_combo.set(config.default_waveform.value)
    waveform_combo.grid(row=0, column=1, padx=5, pady=5)
    waveform_combo.bind("<<ComboboxSelected>>", on_waveform_change)

    # Pulse Width
    pulse_frame = ttk.LabelFrame(frame, text="Pulse Width")
    ttk.Label(pulse_frame, text="Width:").grid(row=0, column=0)
    pulse_label = ttk.Label(pulse_frame, text=f"{config.pulse_width:.2f}")
    pulse_label.grid(row=0, column=2)
    pulse_scale = ttk.Scale(pulse_frame, from_=0.1, to=0.9)
    if on_pulse is not None:
        pulse_scale.config(command=lambda v: on_pulse(v, pulse_label))
    pulse_scale.set(config.pulse_width)
    pulse_scale.grid(row=0, column=1)
    pulse_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w')

    # Super Saw
    super_saw_frame = ttk.LabelFrame(frame, text="Super Saw")
    ttk.Label(super_saw_frame, text="Voices:").grid(row=0, column=0)
    ss_voices_label = ttk.Label(super_saw_frame, text=str(config.super_saw_voices))
    ss_voices_label.grid(row=0, column=2)
    ss_voices = ttk.Scale(super_saw_frame, from_=2, to=12)
    if on_ss_voices is not None:
        ss_voices.config(command=lambda v: on_ss_voices(int(round(float(v))), ss_voices_label))
    ss_voices.set(config.super_saw_voices)
    ss_voices.grid(row=0, column=1)
    super_saw_frame.grid(row=2, column=0, padx=5, pady=5, sticky='w')

    frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    return {
        "frame": frame,
        "waveform_combo": waveform_combo,
        "pulse_frame": pulse_frame,
        "pulse_label": pulse_label,
        "pulse_scale": pulse_scale,
        "super_saw_frame": super_saw_frame,
        "ss_voices_label": ss_voices_label,
        "ss_voices": ss_voices,
    }

def create_envelope_controls(parent, config, on_adsr_change, on_curve_change):
    
    """
    Cria e retorna os controles de envelope ADSR para a interface gráfica.

    Esta função monta sliders para Attack, Decay, Sustain, Release e seleção do tipo de curva.

    Parâmetros:
        parent: Widget pai onde os controles serão inseridos.
        config: Objeto de configuração do sintetizador.
        on_adsr_change: Callback para alteração dos parâmetros ADSR.
        on_curve_change: Callback para alteração do tipo de curva.

    Retorna:
        tuple: (frame, sliders, labels, curve_combo) com referências aos widgets criados.
    """
    
    frame = ttk.LabelFrame(parent, text="Envelope ADSR")
    sliders = {}
    labels = {}

    adsr_params = [
        ('Attack', 0.0, 2.0, config.attack_time),
        ('Decay', 0.0, 2.0, config.decay_time),
        ('Sustain', 0.0, 1.0, config.sustain_level),
        ('Release', 0.0, 2.0, config.release_time)
    ]

    for i, (name, min_val, max_val, init_val) in enumerate(adsr_params):
        ttk.Label(frame, text=f"{name}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
        label = ttk.Label(frame, text=f"{init_val:.2f}")
        label.grid(row=i, column=2, sticky="e", padx=5, pady=5)
        slider = ttk.Scale(
            frame, from_=min_val, to=max_val,
            command=lambda v, n=name.lower(), l=label: on_adsr_change(n, float(v), l)
        )
        slider.set(init_val)
        slider.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
        sliders[name.lower()] = slider
        labels[name.lower()] = label
        frame.rowconfigure(i, weight=1)

    # ADSR Curve Type
    ttk.Label(frame, text="Curve Type:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    curve_combo = ttk.Combobox(frame, values=['Linear', 'Exponential'], state="readonly")
    curve_combo.set(config.adsr_curve.value.capitalize())
    curve_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
    curve_combo.bind('<<ComboboxSelected>>', on_curve_change)

    frame.columnconfigure(1, weight=1)
    frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    return frame, sliders, labels, curve_combo

def create_modulation_controls(
    parent, config,
    on_fm_freq, on_fm_index, on_additive,
    on_lfo_freq, on_lfo_depth, on_lfo_target,
    on_hfo_freq, on_hfo_depth, on_hfo_target,
    on_filter_type, on_filter_freq, on_filter_q
):
    """
    Cria e retorna os controles de modulação e filtros para a interface gráfica.

    Esta função monta sliders e combos para FM, harmônicos aditivos, LFO, HFO e filtros digitais.

    Parâmetros:
        parent: Widget pai onde os controles serão inseridos.
        config: Objeto de configuração do sintetizador.
        on_fm_freq: Callback para frequência FM.
        on_fm_index: Callback para índice FM.
        on_additive: Callback para harmônicos aditivos.
        on_lfo_freq: Callback para frequência LFO.
        on_lfo_depth: Callback para profundidade LFO.
        on_lfo_target: Callback para alvo LFO.
        on_hfo_freq: Callback para frequência HFO.
        on_hfo_depth: Callback para profundidade HFO.
        on_hfo_target: Callback para alvo HFO.
        on_filter_type: Callback para tipo de filtro.
        on_filter_freq: Callback para frequência de corte do filtro.
        on_filter_q: Callback para Q do filtro.

    Retorna:
        dict: Dicionário com referências aos widgets criados.
    """
    frame = ttk.LabelFrame(parent, text="Modulação/Filtros")

    # FM Frequency
    ttk.Label(frame, text="FM Frequency:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    fm_freq_label = ttk.Label(frame, text=f"{config.fm_mod_freq:.1f}")
    fm_freq_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)
    fm_freq = ttk.Scale(frame, from_=0.1, to=5000, command=on_fm_freq)
    fm_freq.set(config.fm_mod_freq)
    fm_freq.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    # FM Index
    ttk.Label(frame, text="FM Index:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    fm_index_label = ttk.Label(frame, text=f"{config.fm_mod_index:.2f}")
    fm_index_label.grid(row=1, column=2, sticky="e", padx=5, pady=5)
    fm_index = ttk.Scale(frame, from_=0, to=10, command=on_fm_index)
    fm_index.set(config.fm_mod_index)
    fm_index.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    # Additive Harmonics
    ttk.Label(frame, text="Additive Harmonics:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    additive_label = ttk.Label(frame, text=str(config.additive_harmonics))
    additive_label.grid(row=2, column=2, sticky="e", padx=5, pady=5)
    additive_scale = ttk.Scale(frame, from_=1, to=16, command=on_additive)
    additive_scale.set(config.additive_harmonics)
    additive_scale.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # LFO
    ttk.Label(frame, text="LFO Freq:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    lfo_freq_label = ttk.Label(frame, text=f"{config.lfo_freq:.2f} Hz")
    lfo_freq_label.grid(row=3, column=2, sticky="e", padx=5, pady=5)
    lfo_freq = ttk.Scale(frame, from_=0.1, to=20.0, command=on_lfo_freq)
    lfo_freq.set(config.lfo_freq)
    lfo_freq.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame, text="LFO Depth:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    lfo_depth_label = ttk.Label(frame, text=f"{config.lfo_depth:.2f}")
    lfo_depth_label.grid(row=4, column=2, sticky="e", padx=5, pady=5)
    lfo_depth = ttk.Scale(frame, from_=0.0, to=1.0, command=on_lfo_depth)
    lfo_depth.set(config.lfo_depth)
    lfo_depth.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame, text="LFO Target:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    lfo_target = ttk.Combobox(frame, values=["pitch", "pulse"])
    lfo_target.set(config.lfo_target)
    lfo_target.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
    lfo_target.bind('<<ComboboxSelected>>', on_lfo_target)

    # HFO
    ttk.Label(frame, text="HFO Freq:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    hfo_freq_label = ttk.Label(frame, text=f"{config.hfo_freq:.1f} Hz")
    hfo_freq_label.grid(row=6, column=2, sticky="e", padx=5, pady=5)
    hfo_freq = ttk.Scale(frame, from_=20, to=8000, command=on_hfo_freq)
    hfo_freq.set(config.hfo_freq)
    hfo_freq.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame, text="HFO Depth:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    hfo_depth_label = ttk.Label(frame, text=f"{config.hfo_depth:.2f}")
    hfo_depth_label.grid(row=7, column=2, sticky="e", padx=5, pady=5)
    hfo_depth = ttk.Scale(frame, from_=0.0, to=1.0, command=on_hfo_depth)
    hfo_depth.set(config.hfo_depth)
    hfo_depth.grid(row=7, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame, text="HFO Target:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
    hfo_target = ttk.Combobox(frame, values=["pitch"])
    hfo_target.set(config.hfo_target)
    hfo_target.grid(row=8, column=1, sticky="ew", padx=5, pady=5)
    hfo_target.bind('<<ComboboxSelected>>', on_hfo_target)

    # FILTER
    filter_frame = ttk.LabelFrame(frame, text="Filter")
    filter_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky='ew')
    filter_frame.columnconfigure(1, weight=1)

    ttk.Label(filter_frame, text="Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    filter_type = ttk.Combobox(filter_frame, values=["lowpass", "highpass", "bandpass"])
    filter_type.set(config.filter_type)
    filter_type.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    filter_type.bind("<<ComboboxSelected>>", on_filter_type)

    ttk.Label(filter_frame, text="Cutoff (Hz):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    filter_freq_label = ttk.Label(filter_frame, text=f"{config.filter_freq:.0f}")
    filter_freq_label.grid(row=1, column=2, sticky="e", padx=5, pady=5)
    filter_freq = ttk.Scale(filter_frame, from_=1, to=config.sample_rate//2 - 1, command=on_filter_freq)
    filter_freq.set(config.filter_freq)
    filter_freq.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(filter_frame, text="Q:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    filter_q_label = ttk.Label(filter_frame, text=f"{config.filter_q:.2f}")
    filter_q_label.grid(row=2, column=2, sticky="e", padx=5, pady=5)
    filter_q = ttk.Scale(filter_frame, from_=0.1, to=10.0, command=on_filter_q)
    filter_q.set(config.filter_q)
    filter_q.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # Expansão das colunas para sliders
    for i in range(10):
        frame.rowconfigure(i, weight=1)
    frame.columnconfigure(1, weight=1)

    frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # Retorne todos os widgets relevantes para binds e updates
    return {
        "frame": frame,
        "fm_freq": fm_freq, "fm_freq_label": fm_freq_label,
        "fm_index": fm_index, "fm_index_label": fm_index_label,
        "additive_scale": additive_scale, "additive_label": additive_label,
        "lfo_freq": lfo_freq, "lfo_freq_label": lfo_freq_label,
        "lfo_depth": lfo_depth, "lfo_depth_label": lfo_depth_label,
        "lfo_target": lfo_target,
        "hfo_freq": hfo_freq, "hfo_freq_label": hfo_freq_label,
        "hfo_depth": hfo_depth, "hfo_depth_label": hfo_depth_label,
        "hfo_target": hfo_target,
        "filter_type": filter_type,
        "filter_freq": filter_freq, "filter_freq_label": filter_freq_label,
        "filter_q": filter_q, "filter_q_label": filter_q_label,
        "filter_frame": filter_frame
    }

def create_system_controls(parent, config, on_sample_rate, on_buffer_size, on_polyphony, on_save, on_load, on_wavetable):
    frame = ttk.LabelFrame(parent, text="Sistema")

    """
    Cria e retorna os controles de sistema para a interface gráfica.

    Esta função monta controles para seleção de dispositivo MIDI, polifonia, sample rate, buffer size e botões de salvar/carregar configuração.

    Parâmetros:
        parent: Widget pai onde os controles serão inseridos.
        config: Objeto de configuração do sintetizador.
        on_sample_rate: Callback para alteração do sample rate.
        on_buffer_size: Callback para alteração do buffer size.
        on_polyphony: Callback para alteração da polifonia máxima.
        on_save: Callback para salvar configuração.
        on_load: Callback para carregar configuração.
        on_wavetable: Callback para carregar wavetable.

    Retorna:
        dict: Dicionário com referências aos widgets criados.
    """

    # MIDI Devices (opcional, se usar mido)
    try:
        import mido
        midi_inputs = mido.get_input_names()
    except ImportError:
        midi_inputs = []
    ttk.Label(frame, text="MIDI Input:").grid(row=0, column=0)
    midi_devices = ttk.Combobox(frame, values=midi_inputs, state="readonly")
    midi_devices.grid(row=0, column=1)

    # Polyphony
    ttk.Label(frame, text="Max Polyphony:").grid(row=1, column=0)
    polyphony_label = ttk.Label(frame, text=str(config.max_polyphony))
    polyphony_label.grid(row=1, column=2)
    polyphony = ttk.Scale(frame, from_=1, to=64, command=lambda v: on_polyphony(v, polyphony_label))
    polyphony.set(config.max_polyphony)
    polyphony.grid(row=1, column=1)

    # Wavetable Loader
    ttk.Button(frame, text="Load Wavetable", command=on_wavetable).grid(row=2, column=0)

     # Sample Rate
    ttk.Label(frame, text="Sample Rate (Hz):").grid(row=3, column=0)
    sample_rate = ttk.Combobox(frame, values=[22050, 32000, 44100, 48000, 96000], state="readonly")
    sample_rate.set(config.sample_rate)
    sample_rate.grid(row=3, column=1)
    # Chame o callback apenas com o evento (ou sem argumentos, se preferir)
    sample_rate.bind('<<ComboboxSelected>>', on_sample_rate)

    # Buffer Size
    ttk.Label(frame, text="Buffer Size:").grid(row=4, column=0)
    buffer_size = ttk.Combobox(frame, values=[32, 64, 128, 256, 512], state="readonly")
    buffer_size.set(config.buffer_size)
    buffer_size.grid(row=4, column=1)
    buffer_size.bind('<<ComboboxSelected>>', on_buffer_size)

    # Config buttons
    ttk.Button(frame, text="Salvar Configuração", command=lambda: on_save()).grid(row=5, column=0, pady=10)
    ttk.Button(frame, text="Carregar Configuração", command=lambda: on_load()).grid(row=5, column=1, pady=10)

    frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    return {
        "frame": frame,
        "midi_devices": midi_devices,
        "polyphony": polyphony,
        "polyphony_label": polyphony_label,
        "sample_rate": sample_rate,
        "buffer_size": buffer_size
    }