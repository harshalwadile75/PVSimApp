import json

def save_config(config, filename="project_config.json"):
    with open(filename, "w") as f:
        json.dump(config, f, indent=4)
    return filename

def load_config(file):
    content = file.read()
    config = json.loads(content)
    return config
