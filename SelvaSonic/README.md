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
