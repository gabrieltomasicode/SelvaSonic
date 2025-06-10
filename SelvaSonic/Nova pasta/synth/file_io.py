<<<<<<< HEAD
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
=======
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
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    return config