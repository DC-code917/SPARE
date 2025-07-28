import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

# Set output root directory
output_root = Path("/root/intent_mcd")
output_root.mkdir(parents=True, exist_ok=True)

# Traverse all .xml files in the current directory
for filename in os.listdir('.'):
    if filename.lower().endswith(".xml"):
        print(f"Processing file: {filename}")
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"  ✖ Failed to parse XML file: {filename}, error: {e}")
            continue

        # Map: apiArg value => list of <action> elements
        value_to_actions = defaultdict(list)

        for action in root.findall(".//action"):
            for api_arg in action.findall(".//apiArg"):
                val = api_arg.get("value")
                if val:
                    try:
                    
                        value_numeric = int(val, 16) if val.startswith("0x") else int(val)
                        if value_numeric > 1000:
                            value_to_actions[val].append(action)
                    except ValueError:
                        continue  

     
        repeated_values = {val: acts for val, acts in value_to_actions.items() if len(acts) > 1}

        sample_name = Path(filename).stem
        sample_dir = output_root / sample_name
        sample_dir.mkdir(parents=True, exist_ok=True)

        for val, actions in repeated_values.items():
            api_names = {action.get("api_name") for action in actions}
            if len(api_names) == 1:
                continue

   
            new_root = ET.Element("matching_actions", attrib={"apiArg_value": val})
            for action in actions:
                new_root.append(action)

            out_path = sample_dir / f"{val}.xml"
            new_tree = ET.ElementTree(new_root)
            new_tree.write(out_path, encoding='utf-8', xml_declaration=True)
           
