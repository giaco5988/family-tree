import os


def update_file_name(file_path: str) -> str:
    """
    Append file version number to filename
    :param file_path: file path without version number
    :return: file path with version number
    """
    file_dir = os.path.dirname(file_path)
    filename, ext = os.path.splitext(os.path.basename(file_path))

    count = 0
    new_filename = os.path.join(file_dir, filename + f"_{count}" + ext)
    while os.path.isfile(new_filename):
        count += 1
        new_filename = os.path.join(file_dir, filename + f"_{count}" + ext)

    return new_filename
