<div align="center">
  <h1>🎹 SelvaSonic</h1>
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=500&size=22&pause=1000&color=FF5733&center=true&vCenter=true&width=600&lines=Softsynth+Modular+em+Python;Audio+DSP+%26+Design+Sonoro;Polifonia,+ADSR+%26+Controle+MIDI" alt="Typing SVG" />
  </a>
</div>

<p align="center">
  <strong>Sintetizador de áudio via software (Softsynth) desenvolvido em Python.</strong>
</p>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Audio_DSP-FF8C00?style=for-the-badge&logo=audio-technica&logoColor=white" alt="DSP" />
  <img src="https://img.shields.io/badge/MIDI-4B0082?style=for-the-badge&logo=midi&logoColor=white" alt="MIDI" />
  <img src="https://img.shields.io/badge/UML-00599C?style=for-the-badge&logo=uml&logoColor=white" alt="UML Software Engineering" />
</div>

<br>

O **SelvaSonic** visa criar uma interface musical rica e modular, oferecendo controle detalhado sobre a geração de som, filtros, envelopes e modulação, além de integração com controladores MIDI. 

Este repositório não contém apenas o código-fonte, mas também toda a base de documentação de engenharia de software (diagramas UML) que guiou a arquitetura do sistema.

---

## 🎯 Funcionalidades Principais

O motor de síntese (`synth/`) e a interface gráfica (`ui/`) foram construídos de forma modular, suportando as seguintes funcionalidades:

* 🔊 **Motor de Áudio & Polifonia:** Suporte a múltiplas vozes simultâneas para a execução de acordes complexos.
* 🌊 **Múltiplos Osciladores (Waveforms & Wavetables):** Inclui formas de onda padrão e *wavetables* personalizáveis.
* ⚡ **Osciladores Especiais:** Oscilador *Supersaw* (ideal para timbres densos e eletrônicos), além de controles de pulso (Pulse/PWM) e síntese aditiva.
* 🎛️ **Modelagem Sonora (Filtros):** Módulos dedicados para corte e manipulação de frequências.
* 📈 **Modelagem Sonora (Envelopes ADSR):** Controle preciso de ataque, decaimento, sustentação e repouso do som.
* 🔄 **Modelagem Sonora (Modulação):** Matriz de modulação para dar movimento dinâmico ao timbre.
* 🎹 **Integração MIDI:** Suporte nativo para conexão de teclados e controladores MIDI externos.
* 🖥️ **Interface Gráfica (UI):** Painel de controle visual incluindo um teclado virtual interativo, visualizadores de onda (visuals) e widgets modulares para cada seção do sintetizador.

---

## 📂 Estrutura do Repositório

A arquitetura do projeto está dividida em documentação, protótipos e o código de produção. 

<details>
<summary><b>🔍 Clique aqui para expandir e visualizar a árvore de diretórios</b></summary>

```text
SelvaSonic/
│
├── Documentação_antiga/           # Documentação de Engenharia de Software
│   ├── Diagrama de Classes.png    # Arquitetura Orientada a Objetos
│   ├── Diagrama de Componentes.png# Estrutura de módulos
│   ├── Diagrama de Casos de uso.png # Interações do usuário
│   ├── Diagrama de Sequencia.png  # Fluxo de dados no tempo
│   └── Diagrama de Implantação.png# Topologia do sistema
│
├── protótipo_inicial/             # Primeiras versões (AudioSynth.py, SynthInterface.py)
│
└── SelvaSonicScripts/             # Código-fonte principal da versão final
    ├── main.py                    # Ponto de entrada da aplicação
    ├── cleancache.py              # Script utilitário
    ├── synth/                     # Motor de áudio (core)
    │   ├── audio.py, midi.py, polyphony.py, envelopes.py, waveforms.py...
    ├── ui/                        # Interface Gráfica e Widgets
    │   ├── interface.py, keyboard.py, visuals.py
    │   └── controls/              # Controles modulares (Supersaw, Pulse, Filter, etc.)
    └── tests/                     # Suíte de testes unitários
```

</details>

---

## 🚀 Como Executar o Projeto

> **Nota:** Como as bibliotecas específicas não estavam no zip, certifique-se de ajustar este bloco caso use bibliotecas de interface ou áudio específicas (como PyQt5, Tkinter, SoundDevice, Mido, etc).

### Pré-requisitos

* Python 3.x
* Recomenda-se o uso de um ambiente virtual (`venv`).

### Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/gabrieltomasicode/SelvaSonic.git
```

2. Acesse o diretório do projeto:
```bash
cd SelvaSonic
```

3. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

4. Para iniciar o sintetizador e abrir a interface gráfica, execute o script principal localizado na pasta de scripts:
```bash
python SelvaSonicScripts/main.py
```

---

## ✒️ Autor

<div align="center">
  <strong>Gabriel Tomasi de Melo</strong><br>
  <em>Estudante de Análise e Desenvolvimento de Sistemas na Universidade do Vale do Rio dos Sinos (Unisinos).</em>
  <br><br>
  <a href="https://github.com/gabrieltomasicode">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile" />
  </a>
</div>
