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




def random_tid_value(API: str):

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