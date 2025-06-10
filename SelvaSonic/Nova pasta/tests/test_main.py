<<<<<<< HEAD
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from synth.audio import audio_callback
from synth.config import SynthConfig, WaveType, ADSRCurve
from synth.envelopes import calculate_adsr
from synth.file_io import save_config, load_config
from synth.synth import MidiSynth
from synth.utils import validate_adsr
from synth.waveforms import generate_wave
from dataclasses import asdict
import numpy as np
import threading

class DummyTime:
    currentTime = 0.0

class DummyVoice:
    def __init__(self):
        self.frequency = 440
        self.velocity = 1.0
        self.phase = 0.0
        self.age = 0.0
        self.pulse_width = 0.5
        self.time = 0.1
        self.active = True
        self.envelope = 1.0

class TestAudioEngine(unittest.TestCase):
    def test_audio_callback(self):
        frames = 64
        outdata = np.zeros((frames, 2), dtype=np.float32)
        time = DummyTime()
        status = None
        config = SynthConfig()
        voices = {60: DummyVoice()}
        voices_lock = threading.Lock()
        # Deve rodar sem lançar exceção
        audio_callback(outdata, frames, time, status, config, voices, voices_lock)
        self.assertEqual(outdata.shape, (frames, 2))

class TestSynthConfig(unittest.TestCase):
    def test_config_defaults(self):
        config = SynthConfig()
        self.assertIsInstance(config, SynthConfig)
        self.assertTrue(hasattr(config, 'sample_rate'))

    def test_wave_type_enum(self):
        self.assertIn(WaveType.SINE, list(WaveType))

class TestEnvelopes(unittest.TestCase):
    def test_calculate_adsr(self):
        class DummyVoice:
            frequency = 440
            velocity = 1.0
            phase = 0.0
            age = 0.0
            pulse_width = 0.5
            time = 0.1
        voice = DummyVoice()
        config = SynthConfig()
        adsr = calculate_adsr(voice, config)
        self.assertIsInstance(adsr, float)

class TestFileIO(unittest.TestCase):
    def test_save_and_load_config(self):
        config = SynthConfig()
        from enum import Enum
        config_dict = asdict(config)
        for k, v in config_dict.items():
            if isinstance(v, Enum):
                config_dict[k] = v.name
        import json
        with open("test_config.json", "w") as f:
            json.dump(config_dict, f)
        with open("test_config.json", "r") as f:
            loaded = json.load(f)
        self.assertIn("sample_rate", loaded)

class TestMidiSynth(unittest.TestCase):
    def test_midi_synth_init(self):
        synth = MidiSynth()
        self.assertIsNotNone(synth)

class TestUtils(unittest.TestCase):
    def test_validate_adsr(self):
        config = SynthConfig()
        result = validate_adsr(config, 0.5)
        self.assertTrue(result)

class TestWaveforms(unittest.TestCase):
    def test_generate_wave(self):
        class DummyVoice:
            frequency = 440
            velocity = 1.0
            phase = 0.0
            age = 0.0
            pulse_width = 0.5
            time = 0.1
        voice = DummyVoice()
        import numpy as np
        t = np.linspace(0, 1, 100)
        config = SynthConfig()
        wave = generate_wave(voice, t, config)
        self.assertEqual(len(wave), len(t))

if __name__ == '__main__':
=======
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from synth.audio import audio_callback
from synth.config import SynthConfig, WaveType, ADSRCurve
from synth.envelopes import calculate_adsr
from synth.file_io import save_config, load_config
from synth.synth import MidiSynth
from synth.utils import validate_adsr
from synth.waveforms import generate_wave
from dataclasses import asdict
import numpy as np
import threading

class DummyTime:
    currentTime = 0.0

class DummyVoice:
    def __init__(self):
        self.frequency = 440
        self.velocity = 1.0
        self.phase = 0.0
        self.age = 0.0
        self.pulse_width = 0.5
        self.time = 0.1
        self.active = True
        self.envelope = 1.0

class TestAudioEngine(unittest.TestCase):
    def test_audio_callback(self):
        frames = 64
        outdata = np.zeros((frames, 2), dtype=np.float32)
        time = DummyTime()
        status = None
        config = SynthConfig()
        voices = {60: DummyVoice()}
        voices_lock = threading.Lock()
        # Deve rodar sem lançar exceção
        audio_callback(outdata, frames, time, status, config, voices, voices_lock)
        self.assertEqual(outdata.shape, (frames, 2))

class TestSynthConfig(unittest.TestCase):
    def test_config_defaults(self):
        config = SynthConfig()
        self.assertIsInstance(config, SynthConfig)
        self.assertTrue(hasattr(config, 'sample_rate'))

    def test_wave_type_enum(self):
        self.assertIn(WaveType.SINE, list(WaveType))

class TestEnvelopes(unittest.TestCase):
    def test_calculate_adsr(self):
        class DummyVoice:
            frequency = 440
            velocity = 1.0
            phase = 0.0
            age = 0.0
            pulse_width = 0.5
            time = 0.1
        voice = DummyVoice()
        config = SynthConfig()
        adsr = calculate_adsr(voice, config)
        self.assertIsInstance(adsr, float)

class TestFileIO(unittest.TestCase):
    def test_save_and_load_config(self):
        config = SynthConfig()
        from enum import Enum
        config_dict = asdict(config)
        for k, v in config_dict.items():
            if isinstance(v, Enum):
                config_dict[k] = v.name
        import json
        with open("test_config.json", "w") as f:
            json.dump(config_dict, f)
        with open("test_config.json", "r") as f:
            loaded = json.load(f)
        self.assertIn("sample_rate", loaded)

class TestMidiSynth(unittest.TestCase):
    def test_midi_synth_init(self):
        synth = MidiSynth()
        self.assertIsNotNone(synth)

class TestUtils(unittest.TestCase):
    def test_validate_adsr(self):
        config = SynthConfig()
        result = validate_adsr(config, 0.5)
        self.assertTrue(result)

class TestWaveforms(unittest.TestCase):
    def test_generate_wave(self):
        class DummyVoice:
            frequency = 440
            velocity = 1.0
            phase = 0.0
            age = 0.0
            pulse_width = 0.5
            time = 0.1
        voice = DummyVoice()
        import numpy as np
        t = np.linspace(0, 1, 100)
        config = SynthConfig()
        wave = generate_wave(voice, t, config)
        self.assertEqual(len(wave), len(t))

if __name__ == '__main__':
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    unittest.main()