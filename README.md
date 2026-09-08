# SelvaSonic 🎹🔊

**SelvaSonic** é um sintetizador de áudio via software (Softsynth) desenvolvido em Python. O projeto visa criar uma interface musical rica e modular, oferecendo controle detalhado sobre a geração de som, filtros, envelopes e modulação, além de integração com controladores MIDI. 

Este repositório não contém apenas o código-fonte, mas também toda a base de documentação de engenharia de software (diagramas UML) que guiou a arquitetura do sistema.

## 🎯 Funcionalidades Principais

O motor de síntese (`synth/`) e a interface gráfica (`ui/`) foram construídos de forma modular, suportando as seguintes funcionalidades:

*   **Motor de Áudio & Polifonia:** Suporte a múltiplas vozes simultâneas (polifonia) para a execução de acordes complexos.
*   **Múltiplos Osciladores:**
    *   Formas de onda padrão (Waveforms).
    *   *Wavetables* personalizáveis.
    *   Oscilador *Supersaw* (ideal para timbres densos e eletrônicos).
    *   Controles de pulso (Pulse/PWM) e síntese aditiva.
*   **Modelagem Sonora (Sound Shaping):**
    *   **Filtros (Filters):** Módulos dedicados para corte de frequências.
    *   **Envelopes (ADSR):** Controle de ataque, decaimento, sustentação e repouso do som.
    *   **Modulação:** Matriz de modulação para dar movimento dinâmico ao timbre.
*   **Integração MIDI:** Suporte nativo para conexão de teclados e controladores MIDI externos.
*   **Interface Gráfica (UI):** Painel de controle visual incluindo um teclado virtual interativo, visualizadores de onda (visuals) e widgets modulares para cada seção do sintetizador.

## 📂 Estrutura do Repositório

A arquitetura do projeto está dividida em documentação, protótipos e o código de produção:

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

## 🚀 Como Executar o Projeto

*(Nota: Como as bibliotecas específicas não estavam no zip, certifique-se de ajustar este bloco caso use PyQt5, Tkinter, SoundDevice, Mido, etc).*

### Pré-requisitos

*   Python 3.x
*   Recomenda-se o uso de um ambiente virtual (`venv`).

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/gabrieltomasicode/SelvaSonic.git
   ```
2. Acesse o diretório:
   ```bash
   cd SelvaSonic
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Execução

Para iniciar o sintetizador e abrir a interface gráfica, execute o script principal localizado na pasta de scripts:

```bash
python SelvaSonicScripts/main.py
```

## ✒️ Autor

*   **Gabriel Tomasi de Melo**
*   Estudante de Análise e Desenvolvimento de Sistemas na Universidade do Vale do Rio dos Sinos (Unisinos).
*   GitHub: [@gabrieltomasicode](https://github.com/gabrieltomasicode)
