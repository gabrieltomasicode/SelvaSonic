import json
from dataclasses import asdict, fields

def save_config(config, filename="synth_config.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=4)

def load_config(config, filename="synth_config.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        for field in fields(config):
            if field.name in data:
                setattr(config, field.name, data[field.name])
    return config