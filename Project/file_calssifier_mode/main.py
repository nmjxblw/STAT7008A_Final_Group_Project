from Project.file_calssifier_mode.pdf_analysis import pdf_analysis
from Project.file_calssifier_mode.pdf_split_and_embed import pdf_split_and_embed


def start_file_calssify_task(root_dir="./"):
    unclassified_folder=root_dir+"Resource/Unclassified"
    embed_file_folder=root_dir+"DB/embedding"
    pdf_analysis(unclassified_folder)
    pdf_split_and_embed(root_dir,embed_file_folder)


if __name__ == "__main__":
    start_file_calssify_task(root_dir="./")