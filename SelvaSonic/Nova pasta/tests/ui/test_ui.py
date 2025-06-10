import unittest
from ui.interface import FullSynthInterface
from ui.keyboard import KeyboardMIDI
from ui.visuals import generate_static_wave, update_waveform_plot
from ui.widgets import (
    create_oscillator_controls,
    create_envelope_controls,
    create_modulation_controls,
    create_system_controls,
)
from ui.decorators import validate_positive
import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class DummyMaster(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Não mostra janela real nos testes

class TestFullSynthInterface(unittest.TestCase):
    def test_init(self):
        master = DummyMaster()
        interface = FullSynthInterface(master)
        self.assertIsInstance(interface, FullSynthInterface)

class TestKeyboardMIDI(unittest.TestCase):
    def test_init(self):
        master = DummyMaster()
        # Passe um objeto synth mock ou dummy se necessário
        class DummySynth: pass
        midi = KeyboardMIDI(DummySynth(), master)
        self.assertIsInstance(midi, KeyboardMIDI)

class TestVisuals(unittest.TestCase):
    def test_generate_static_wave(self):
        result = generate_static_wave()
        self.assertIsNotNone(result)

    def test_update_waveform_plot(self):
        # Passe argumentos mínimos necessários
        self.assertIsNone(update_waveform_plot(None, None, None))

class TestWidgets(unittest.TestCase):
    def test_create_oscillator_controls(self):
        master = DummyMaster()
        result = create_oscillator_controls(master, None, None, None, None, None)
        self.assertIsNotNone(result)

    def test_create_envelope_controls(self):
        master = DummyMaster()
        result = create_envelope_controls(master, None, None, None)
        self.assertIsNotNone(result)

    def test_create_modulation_controls(self):
        master = DummyMaster()
        result = create_modulation_controls(master, None, None, None)
        self.assertIsNotNone(result)

    def test_create_system_controls(self):
        master = DummyMaster()
        # Passe dummies para todos os callbacks
        result = create_system_controls(master, None, lambda *a, **k: None, lambda *a, **k: None, lambda *a, **k: None, lambda *a, **k: None, lambda *a, **k: None, lambda *a, **k: None)
        self.assertIsNotNone(result)

class TestSanity(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(True)

class TestDecorators(unittest.TestCase):
    def test_validate_positive_ok(self):
        @validate_positive
        def add(a, b):
            return a + b
        self.assertEqual(add(2, 3), 5)

    def test_validate_positive_negative(self):
        @validate_positive
        def add(a, b):
            return a + b
        with self.assertRaises(ValueError):
            add(-1, 2)