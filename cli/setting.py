import json

def set(ctx, key, value):
    with open(ctx.setting_file, 'r+') as f:
        data = json.load(f)
        f.seek(0)
        f.truncate()
        data[key] = value
        json.dump(data, f)

def get(ctx):
    with open(ctx.setting_file, 'r') as f:
        return json.load(f)
