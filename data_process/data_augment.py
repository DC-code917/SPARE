import os
import random
import shutil
import json, operator
import pickle
import multiprocessing as mp
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
import string
from tqdm import tqdm



def random_handle_value(API: str, keys={"Handle", "FileHandle"}):

    api_data = json.loads(API)
    value_mapping = {} 

    def generate_new_hex():
        return "0x" + format(random.randint(0x1000, 0xFFFFF), '08x')

    for call in api_data.get("calls", []):
        for arg in call.get("arguments", []):
            name = arg.get("name", "").lower()
            if name in keys:
                old_val = arg.get("value")
                if isinstance(old_val, str) and old_val.startswith("0x"):
                    if old_val not in value_mapping:
                        value_mapping[old_val] = generate_new_hex()
                    arg["value"] = value_mapping[old_val]
    
    return json.dumps(api_data, indent=4)




def random_ptid_value(API: str):

    api_data = json.loads(API)
    
    tid_map = {}  
    used_values = set()

    def generate_valid_tid():
        while True:
            new_tid = str(random.randint(100, 65535))
            if new_tid not in used_values:
                used_values.add(new_tid)
                return new_tid

    for call in api_data.get("calls", []):
        orig_tid = call.get("thread_id", "")
        if orig_tid not in tid_map:
            tid_map[orig_tid] = generate_valid_tid()
        call["thread_id"] = tid_map[orig_tid]

    return json.dumps(api_data, indent=4)




def random_address_value(API: str, key="Address"):

    api_data = json.loads(API)
    value_mapping = {}  

    def parse_hex_address(val_str):
        try:
            return int(val_str, 16)
        except:
            return None

    def generate_random_address(in_kernel):
        if in_kernel:
            return "0x" + format(random.randint(0x80000000, 0xFFFFFFFF), '08x')
        else:
            return "0x" + format(random.randint(0x10000, 0x7FFFFFFF), '08x')  

    for call in api_data.get("calls", []):
        for arg in call.get("arguments", []):
            name = arg.get("name", "")
            if key.lower() in name.lower():
                val = arg.get("value", "")
                if isinstance(val, str) and val.startswith("0x"):
                    int_val = parse_hex_address(val)
                    if int_val is None:
                        continue

                    in_kernel = int_val >= 0x80000000
                    if val not in value_mapping:
                        value_mapping[val] = generate_random_address(in_kernel)
                    arg["value"] = value_mapping[val]

    return json.dumps(api_data, indent=4)



def random_file_path(API: str):

    api_data = json.loads(API)
    value_mapping = {}

    def generate_random_name(extension=".tmp"):
        base = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"tmpfile_{base}{extension}"

    def is_registry_path(value):
        return isinstance(value, str) and value.startswith("HKEY")

    for call in api_data.get("calls", []):
        for arg in call.get("arguments", []):
            val = arg.get("value", "")
            if not isinstance(val, str):
                continue
            if is_registry_path(val):
                continue
            if "\\" not in val:
                continue


            parts = val.split("\\")
            if len(parts) >= 2:
                original_name = parts[-1]
                key = val  
                if key not in value_mapping:
 
                    if "." in original_name:
                        ext = "." + original_name.split(".")[-1]
                    else:
                        ext = ""
                    value_mapping[key] = "\\".join(parts[:-1] + [generate_random_name(extension=ext)])
                arg["value"] = value_mapping[key]

    return json.dumps(api_data, indent=4)






def enhance_based_data(path, filename, new_file_path, enhance_factor=1):
    """
    Perform API-level data augmentation on a single JSON file.
    
    Parameters:
    - path: Directory containing the original JSON files.
    - filename: Name of the file to enhance.
    - new_file_path: Directory where the enhanced samples will be saved.
    - enhance_factor: Number of augmented samples to generate per instance.
    """

    # Load the original API sequence from JSON file
    input_file = os.path.join(path, filename)
    with open(input_file, "r", encoding="utf-8") as f:
        try:
            original_data = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON: {filename}")
            return

    # Generate multiple enhanced versions
    for i in range(enhance_factor):
        # Deep copy the original data by re-serializing
        new_instance = json.loads(json.dumps(original_data))

        # Convert to string for the mutation functions
        new_instance_str = json.dumps(new_instance)

        # Apply four perturbation functions sequentially
        new_instance_str = random_file_path(new_instance_str)
        new_instance_str = random_address_value(new_instance_str, key="Address")
        new_instance_str = random_ptid_value(new_instance_str)
        new_instance_str = random_handle_value(new_instance_str, keys={"Handle", "FileHandle"})

        # Parse the modified string back to JSON object
        try:
            enhanced_instance = json.loads(new_instance_str)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode enhanced JSON: {filename} -> augmented {i}")
            continue

        # Create a new filename with augmentation index
        base_name = os.path.splitext(filename)[0]
        new_filename = f"{base_name}_aug{i}.json"
        save_path = os.path.join(new_file_path, new_filename)

        # Save the enhanced JSON object
        with open(save_path, "w", encoding="utf-8") as out_f:
            json.dump(enhanced_instance, out_f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved enhanced sample: {new_filename}")