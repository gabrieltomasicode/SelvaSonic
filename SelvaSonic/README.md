<<<<<<< HEAD
# 🎧 SelvaSonic AudioSynth

Sistema profissional de síntese de áudio MIDI em Python, projetado para aplicações musicais, experimentação sonora e integração com controladores MIDI. Possui uma interface gráfica interativa com suporte a teclado virtual.

## 🚀 Recursos Principais

- 🎹 Suporte a 11 tipos de onda (Sine, Square, Super Saw, Pulse, Noise, Pink/Brown Noise, Wavetable)
- 🧠 Gestão de polifonia com remoção inteligente de vozes
- 🕹️ Envelope ADSR com curvas linear ou exponencial
- 🔊 Modulação FM, LFO e HFO com roteamento flexível (pitch, pulse, volume, etc)
- 🔈 Filtros digitais configuráveis (lowpass, highpass, bandpass)
- 🎛️ Integração MIDI completa (note on/off, pitch bend, control change)
- 🎧 Geração de áudio em tempo real com baixa latência
- 🧩 Arquitetura modular, extensível e orientada a objetos
- 📦 Suporte a síntese aditiva e wavetable customizada

## 📦 Instalação

Recomenda-se o uso de um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

Instale as dependências:

```bash
pip install numpy mido sounddevice soundfile matplotlib pynput scipy
```

## ▶️ Execução

Inicie o sintetizador com interface gráfica:

```bash
python SynthInterface.py
```

## 🎛️ Controles via Teclado

- Teclas do teclado QWERTY controlam as notas
- Teclas numéricas para mudar oitavas
- Detecção automática de MIDI externo se disponível
=======
<<<<<<<< HEAD:README.md
# 🎧 SelvaSonic AudioSynth

**SelvaSonic** é um sintetizador de áudio polifônico e modular em Python, com interface gráfica interativa, suporte MIDI, síntese aditiva, FM, SuperSaw, envelopes avançados, filtros digitais e visualização em tempo real.

---

## 🚀 Funcionalidades

- **Osciladores**: Sine, Square, Triangle, Sawtooth, Pulse, SuperSaw, Noise, Pink/Brown Noise, Wavetable customizada
- **Envelopes**: ADSR com curvas Linear/Exponencial
- **Modulação**: FM, LFO, HFO, modulação de pitch/pulse
- **Filtros**: Lowpass, Highpass, Bandpass, controle de Q dinâmico
- **Polifonia**: Até 8 vozes simultâneas (ajustável)
- **Integração MIDI**: Teclado virtual e suporte a dispositivos MIDI externos
- **Visualização**: Forma de onda em tempo real e preview estático
- **Presets**: Salvar e carregar configurações completas via interface
- **Arquitetura Modular**: Separação clara entre núcleo de síntese, interface, controles e utilitários

---

## 📦 Instalação

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/gabrieltomasicode/SelvaSonic.git
   cd SelvaSonic/Nova\ pasta
   ```

2. **Crie um ambiente virtual (opcional, recomendado)**
   ```bash
   python -m venv venv
   # Ative no Windows:
   venv\Scripts\activate
   # Ou no Linux/macOS:
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install numpy scipy sounddevice mido matplotlib pynput
   ```

---

## ▶️ Como Usar

```bash
python main.py
```

- Use o teclado do computador (A-K, W,E,T,Y,U) ou um teclado MIDI externo para tocar.
- Ajuste parâmetros em tempo real pela interface gráfica.
- Salve e carregue presets de configuração facilmente.

---
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8

## 🗂️ Estrutura do Projeto

```
<<<<<<< HEAD
Backup Synth/
├── AudioSynth.py          # Núcleo do sintetizador
├── SynthInterface.py      # Interface gráfica + controle
├── README.md              # Documentação 
├── Documentação/          # Diagramas e documentação técnica
```

## 📄 Documentação

O diretório `Documentação/` inclui:

- Diagramas de Casos de Uso
- Diagrama de Classes
- Diagrama de Componentes
- Diagrama de Implantação
- Diagrama de Sequência

## 👤 Autor

**Gabriel Tomasi de Melo**  
Versão: 1.3.1  
Data: 20/05/2025
=======
Nova pasta/
├── main.py
├── synth/
│   ├── audio.py
│   ├── config.py
│   ├── envelopes.py
│   ├── file_io.py
│   ├── filters.py
│   ├── midi.py
│   ├── synth.py
│   ├── utils.py
│   ├── voices.py
│   └── waveforms.py
├── ui/
│   ├── interface.py
│   ├── keyboard.py
│   ├── visuals.py
│   ├── widgets.py
│   └── controls/
│       ├── aditive_controls.py
│       ├── envelope_controls.py
│       ├── filter_controls.py
│       ├── modulation_controls.py
│       ├── polyphony_controls.py
│       └── pulse_controls.py
├── tests/
│   └── test_main.py
└── Documentação/
    ├── Diagrama de Classes.png
    ├── Diagrama de Componentes.png
    ├── Diagrama de Casos de Uso.png
    ├── Diagrama de Implantação.png
    └── Diagrama de Sequencia.png
```

---

## 🖼️ Diagrama de Arquitetura (texto)

```
[Usuário]
   │
   ▼
[UI: interface.py, widgets.py, controls/*]
   │
   ▼
[Synth: synth.py, voices.py, audio.py, filters.py, envelopes.py, waveforms.py]
   │
   ├── [MIDI: midi.py]
   ├── [Config: config.py, file_io.py]
   └── [Utils: utils.py]
```

---

## 🎛️ Controles Rápidos

**Teclado Virtual:**
- A-K: Notas naturais
- W,E,T,Y,U: Sustenidos
- -/= : Troca de oitava

**Interface:**
- Sliders e combos para todos os parâmetros
- Salvar/Carregar preset
- Visualização da forma de onda

---

## 👤 Autor

Gabriel Tomasi de Melo  
Versão: 2.5.1  
Data: 10/06/2025

---

## 📄 Documentação

Veja a pasta `Documentação/` para diagramas UML, casos de uso e detalhes técnicos.

---

## 📝 Licença

MIT License 
========
# 🎧 SelvaSonic AudioSynth

Sistema profissional de síntese de áudio MIDI em Python, projetado para aplicações musicais, experimentação sonora e integração com controladores MIDI. Possui uma interface gráfica interativa com suporte a teclado virtual.

## 🚀 Recursos Principais

- 🎹 Suporte a 11 tipos de onda (Sine, Square, Super Saw, Pulse, Noise, Pink/Brown Noise, Wavetable)
- 🧠 Gestão de polifonia com remoção inteligente de vozes
- 🕹️ Envelope ADSR com curvas linear ou exponencial
- 🔊 Modulação FM, LFO e HFO com roteamento flexível (pitch, pulse, volume, etc)
- 🔈 Filtros digitais configuráveis (lowpass, highpass, bandpass)
- 🎛️ Integração MIDI completa (note on/off, pitch bend, control change)
- 🎧 Geração de áudio em tempo real com baixa latência
- 🧩 Arquitetura modular, extensível e orientada a objetos
- 📦 Suporte a síntese aditiva e wavetable customizada

## 📦 Instalação

Recomenda-se o uso de um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

Instale as dependências:

```bash
pip install numpy mido sounddevice soundfile matplotlib pynput scipy
```

## ▶️ Execução

Inicie o sintetizador com interface gráfica:

```bash
python SynthInterface.py
```

## 🎛️ Controles via Teclado

- Teclas do teclado QWERTY controlam as notas
- Teclas numéricas para mudar oitavas
- Detecção automática de MIDI externo se disponível

## 🗂️ Estrutura do Projeto

```
Backup Synth/
├── AudioSynth.py          # Núcleo do sintetizador
├── SynthInterface.py      # Interface gráfica + controle
├── README.md              # Documentação 
├── Documentação/          # Diagramas e documentação técnica
```

## 📄 Documentação

O diretório `Documentação/` inclui:

- Diagramas de Casos de Uso
- Diagrama de Classes
- Diagrama de Componentes
- Diagrama de Implantação
- Diagrama de Sequência

## 👤 Autor

**Gabriel Tomasi de Melo**  
Versão: 1.3.1  
Data: 20/05/2025
>>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8:SelvaSonic/README.md
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
