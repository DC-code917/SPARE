import json
import os
import glob

input_dirs = ["./data/black/", "./data/white/"]
output_base_dir = "./intent/"

key = ["hFile", "hKey", "th32ProcessID", "hMod", "hProcess", "hService", "hDevice"]

def extract_and_save_patten(input_dirs, output_base_dir, keyset):
    for input_dir in input_dirs:
        if not os.path.exists(output_base_dir):
            os.makedirs(output_base_dir)

        for input_path in glob.glob(os.path.join(input_dir, '*.json')):
            file_name = os.path.basename(input_path).split('.')[0]
            specific_output_dir = os.path.join(output_base_dir, file_name)
            if os.path.exists(specific_output_dir):
                print(f"Skipping {input_path} as it has already been processed.")
                continue
            with open(input_path, 'r') as f:
                t = json.load(f)

            procs = t['behavior']['processes']
            for proc in procs:
                calls = proc['calls'][:1000]  # 修改：限制处理到前1000个调用
                for call in calls:
                    if 'api' not in call or call['api'][:2] == '__' or 'arguments' not in call:
                        continue
                    if 'category' not in call:
                        call['category'] = ""
                    if 'status' not in call:
                        call['status'] = 0
                    for arg in call['arguments']:
                        key = arg['name']
                        value = arg['value']
                        if key in keyset:
                            if not os.path.exists(specific_output_dir):
                                os.makedirs(specific_output_dir)
                            append_matching_calls_to_file(key, value, call['category'], procs[:1000], keyset, specific_output_dir)
                            # 注意：这里不再需要对max_len进行操作

def append_matching_calls_to_file(matching_key, matching_value, matching_category, procs, keyset, specific_output_dir):
    matching_calls = []
    for proc in procs:
        count = 0  # 引入计数器以限制匹配次数
        for call in proc['calls']:
            if count >= 1000:  # 若已处理1000个调用，则跳出循环
                break
            if call_matches(call, matching_key, matching_value, matching_category, keyset):
                matching_calls.append(call)
                count += 1  # 更新计数器

    if len(matching_calls) > 1:
        filename = os.path.join(specific_output_dir, f"{matching_category}_{matching_key}_{matching_value}.json")
        with open(filename, 'w') as f:
            json.dump(matching_calls, f, indent=4)


# 示例调用函数
extract_and_save_patten(input_dirs, output_base_dir, key)
