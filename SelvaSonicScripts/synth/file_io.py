import json
from dataclasses import asdict, fields, is_dataclass
from tkinter import filedialog, messagebox

def enum_to_str(obj):
    """
    Converte todos os atributos Enum de um objeto dataclass (ou dicionário) para strings.

    Esta função percorre os campos de um objeto dataclass ou dicionário e, caso algum campo seja uma instância de Enum,
    converte seu valor para o nome da Enum correspondente (string). Isso facilita a serialização para formatos como JSON.

    Parâmetros:
        obj: Objeto dataclass ou dicionário a ser convertido.

    Retorna:
        dict: Dicionário com os valores Enum convertidos para strings.

    Notas:
        - Apenas campos que possuem o atributo 'name' (tipicamente Enums) são convertidos.
        - Os demais campos permanecem inalterados.
    """
    if is_dataclass(obj):
        d = asdict(obj)
    else:
        d = obj
    for k, v in d.items():
        if hasattr(v, "name"):
            d[k] = v.name
    return d

def save_config(config, filename="synth_config.json"):
    """
    Salva a configuração do sintetizador em um arquivo JSON.

    Esta função serializa o objeto de configuração, convertendo Enums para strings, e salva o resultado em um arquivo JSON.
    O arquivo pode ser posteriormente carregado para restaurar as configurações do sintetizador.

    Parâmetros:
        config: Objeto de configuração a ser salvo (dataclass).
        filename (str): Nome do arquivo de saída (padrão: "synth_config.json").
    """
    data = enum_to_str(config)
    
    # NOVO: Proteção Crítica contra Erros de Serialização!
    # Como o JSON nativo do Python não consegue converter arrays do NumPy (np.ndarray),
    # removemos estes objetos temporários da cópia de salvamento para evitar que o programa crashe.
    data.pop("bandlimited_tables", None)
    data.pop("last_audio_buffer", None)
    data.pop("wavetable", None) # Remove também se houver alguma wavetable customizada em memória

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_config(config, filename="synth_config.json"):
    """
    Carrega as configurações do sintetizador a partir de um arquivo JSON.

    Esta função lê um arquivo JSON contendo as configurações do sintetizador, converte strings de volta para Enums quando necessário,
    e atualiza os campos do objeto de configuração fornecido.

    Parâmetros:
        config: Objeto de configuração a ser atualizado (dataclass).
        filename (str): Nome do arquivo de configuração a ser lido (padrão: "synth_config.json").

    Retorna:
        config: O objeto de configuração atualizado com os valores carregados do arquivo.

    Notas:
        - Campos que representam Enums são convertidos de volta para seus respectivos tipos.
        - Se o arquivo não existir ou estiver corrompido, uma mensagem de erro é exibida e o objeto original é retornado.
        - Apenas campos presentes tanto no arquivo quanto no objeto de configuração são atualizados.
    """
    from synth.config import WaveType, ADSRCurve
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for field in fields(config):
                if field.name in data:
                    value = data[field.name]
                    # Converta de volta para Enum se necessário
                    if field.name == "default_waveform" and isinstance(value, str):
                        if value in WaveType.__members__:
                            value = WaveType[value]
                        else:
                            continue
                    elif field.name == "adsr_curve" and isinstance(value, str):
                        if value in ADSRCurve.__members__:
                            value = ADSRCurve[value]
                        else:
                            continue
                    setattr(config, field.name, value)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar configuração: {e}")
    return config

