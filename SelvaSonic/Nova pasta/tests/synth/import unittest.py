import unittest
from synth.config import SynthConfig, load_config, save_config
import numpy as np
import numpy as np

# test_main.py


# audio.py
from synth.audio import (
    get_audio_devices, AudioStream, list_output_devices
)

# config.py

# envelopes.py
from synth.envelopes import (
    ADSREnvelope, calculate_adsr, EnvelopeParams
)

# file_io.py
from synth.file_io import (
    load_wavetable, save_wavetable, read_wav_file, write_wav_file
)

# filters.py
from synth.filters import (
    BiquadFilter, apply_filter, FilterType
)

# midi.py
from synth.midi import (
    MidiInputHandler, list_midi_devices
)

# synth.py
from synth.synth import (
    Synth, SynthVoice, SynthConfig as SynthSynthConfig
)

# utils.py
from synth.utils import (
    midi_to_freq, clamp, db_to_amp
)

# voices.py
from synth.voices import (
    VoiceManager, Voice
)

# waveforms.py
from synth.waveforms import (
    generate_wave, generate_static_wave, WaveformType
)


class TestAudio(unittest.TestCase):
    def test_get_audio_devices(self):
        devices = get_audio_devices()
        self.assertIsInstance(devices, list)

    def test_list_output_devices(self):
        devices = list_output_devices()
        self.assertIsInstance(devices, list)

    def test_audio_stream_init(self):
        stream = AudioStream()
        self.assertIsNotNone(stream)


class TestConfig(unittest.TestCase):
    def test_synth_config_init(self):
        config = SynthConfig()
        self.assertIsNotNone(config)

    def test_load_config(self):
        config = load_config()
        self.assertIsInstance(config, SynthConfig)

    def test_save_config(self):
        config = SynthConfig()
        save_config(config)  # Should not raise


class TestEnvelopes(unittest.TestCase):
    def test_adsr_envelope(self):
        env = ADSREnvelope()
        self.assertIsNotNone(env)

    def test_calculate_adsr(self):
        env = EnvelopeParams()
        result = calculate_adsr(env, 0.5)
        self.assertIsInstance(result, float)


class TestFileIO(unittest.TestCase):
    def test_load_wavetable(self):
        # Should handle file not found gracefully
        with self.assertRaises(Exception):
            load_wavetable("nonexistent.wav")

    def test_save_wavetable(self):
        # Should not raise (dummy data)
        save_wavetable("dummy.wav", [0.0, 1.0, -1.0])

    def test_read_wav_file(self):
        with self.assertRaises(Exception):
            read_wav_file("nonexistent.wav")

    def test_write_wav_file(self):
        write_wav_file("dummy.wav", [0.0, 1.0, -1.0], 44100)


class TestFilters(unittest.TestCase):
    def test_biquad_filter(self):
        filt = BiquadFilter(FilterType.LOWPASS, 44100, 1000, 0.707)
        self.assertIsNotNone(filt)

    def test_apply_filter(self):
        data = [0.0, 1.0, -1.0]
        filt = BiquadFilter(FilterType.LOWPASS, 44100, 1000, 0.707)
        result = apply_filter(data, filt)
        self.assertEqual(len(result), len(data))


class TestMidi(unittest.TestCase):
    def test_list_midi_devices(self):
        devices = list_midi_devices()
        self.assertIsInstance(devices, list)

    def test_midi_input_handler(self):
        handler = MidiInputHandler()
        self.assertIsNotNone(handler)


class TestSynth(unittest.TestCase):
    def test_synth_init(self):
        synth = Synth()
        self.assertIsNotNone(synth)

    def test_synth_voice(self):
        voice = SynthVoice(440, 1.0)
        self.assertIsNotNone(voice)


class TestUtils(unittest.TestCase):
    def test_midi_to_freq(self):
        freq = midi_to_freq(69)
        self.assertAlmostEqual(freq, 440.0, places=1)

    def test_clamp(self):
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-1, 0, 10), 0)
        self.assertEqual(clamp(11, 0, 10), 10)

    def test_db_to_amp(self):
        self.assertAlmostEqual(db_to_amp(0), 1.0, places=2)


class TestVoices(unittest.TestCase):
    def test_voice_manager(self):
        vm = VoiceManager()
        self.assertIsNotNone(vm)

    def test_voice(self):
        v = Voice(440, 1.0)
        self.assertIsNotNone(v)


class TestWaveforms(unittest.TestCase):
    def test_generate_wave(self):
        class DummyVoice:
            freq = 440
            velocity = 1.0
        t = np.linspace(0, 1, 100)
        config = SynthConfig()
        wave = generate_wave(DummyVoice(), t, config)
        self.assertEqual(len(wave), len(t))

    def test_generate_static_wave(self):
        phase = np.linspace(0, 2 * np.pi, 100)
        config = SynthConfig()
        wave = generate_static_wave(phase, config)
        self.assertEqual(len(wave), len(phase))


if __name__ == "__main__":
    unittest.main()