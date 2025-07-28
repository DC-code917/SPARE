import os
import json
from collections import defaultdict
from pathlib import Path

def is_valid_value(val):
    try:
        if val.startswith("0x") or val.startswith("0X"):
            return int(val, 16) > 1000
        return int(val) > 1000
    except:
        return False

# Set output root directory
output_root = Path("/root/intent_sp")
output_root.mkdir(parents=True, exist_ok=True)

# Traverse all subdirectories in the current directory
current_dir = Path(".")
for subdir in current_dir.iterdir():
    if subdir.is_dir():

        for json_file in subdir.glob("*.json"):
            print(f"Processing file: {json_file}")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Failed to read or parse {json_file}: {e}")
                continue

            value_to_apis = defaultdict(list)

            for entry in data:
                apis = entry.get("apis", [])
                for api in apis:
                    args = api.get("args", [])
                    for arg in args:
                        if arg and is_valid_value(arg):
                            value_to_apis[arg].append(api)

      
            repeated_values = {val: apis for val, apis in value_to_apis.items() if len(apis) > 1}


            sample_name = json_file.stem
            sample_dir = output_root / sample_name
            sample_dir.mkdir(parents=True, exist_ok=True)

            for val, matched_apis in repeated_values.items():
  
                api_names = {api.get("api_name") for api in matched_apis}
                if len(api_names) == 1:
                    print(f"Skipping value {val}: all api_name values are identical ({list(api_names)[0]})")
                    continue

                out_path = sample_dir / f"{val}.json"
                try:
                    with open(out_path, 'w', encoding='utf-8') as f_out:
                        json.dump(matched_apis, f_out, indent=2)
                    print(f"Matched value {val} saved to: {out_path}")
                except Exception as e:
                    print(f" Failed to write: {out_path}, error: {e}")
