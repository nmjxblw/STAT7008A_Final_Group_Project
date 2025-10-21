import json
import os
import shutil


def move_files(source, target, success_filename_list):
    """
    根据文件名列表，将源文件夹中存在的对应文件移动到目标文件夹
    """
    try:
        # 检查文件夹
        if not os.path.exists(source):
            raise Exception(f"source folder {source} not exists")

        if not os.path.exists(target):
            os.makedirs(target)

        # 移动文件
        moved_count = 0
        for filename in success_filename_list:
            src_path = os.path.join(source, filename)
            dst_path = os.path.join(target, filename)

            if os.path.exists(src_path):
                shutil.move(src_path, dst_path)
                print(f"Moved: {filename}")
                moved_count += 1
            else:
                print(f"Not found: {filename}")

        print(f"Finished. Moved {moved_count} files")
        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def save_to_json(file_info, save_data_folder):
        """将结果保存到简单的文件数据库中"""
        # 如果数据库文件已存在，加载现有数据
        db_file = save_data_folder + "\\pdf_analysis_database.json"
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                database = json.load(f)
        else:
            database = {}
        database[file_info["file_id"]] = {
            "file_id": file_info["file_id"],
            "file_text": file_info["file_text"],
            "file_name": file_info["file_name"],
            "file_title": file_info["file_title"],
            "file_summary": file_info["file_summary"],
            "file_keywords": file_info["file_keywords"],
        }

        # 保存到JSON文件
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
