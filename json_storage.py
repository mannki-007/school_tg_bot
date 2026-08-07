import json
import os

DB_FILE = 'data.json'


def load_data():
  default_data = {
      'dz_history': [],
      'vazhnoe_history': [],
      'meropriyatiya_history': [],
      'raspisanie': {},
  }

  if not os.path.exists(DB_FILE):
    save_data(default_data)
    return default_data

  try:
    with open(DB_FILE, 'r', encoding='utf-8') as f:
      data = json.load(f)

    updated = False
    for key, value in default_data.items():
      if key not in data:
        data[key] = value
        updated = True

    if updated:
      save_data(data)

    return data
  except (json.decoder.JSONDecodeError, ValueError):
    save_data(default_data)
    return default_data


def save_data(data):
  with open(DB_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)