import os
import json
import config

def merge_json_files(folder_path, output_file):
    merged_data = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json') and file_name != "merged.json":
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                    merged_data.update(data)
                except json.JSONDecodeError as e:
                    print(f"Can not merge {file_name}: {str(e)}")

    with open(output_file, 'w') as file:
        json.dump(merged_data, file)

    print(f"successfully merged!")

if __name__ == "__main__":    
    folder_path = config.output_path
    output_file = 'merged.json'
    merge_json_files(folder_path, output_file)
