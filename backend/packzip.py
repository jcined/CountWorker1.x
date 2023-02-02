import os
import zipfile


def package_to_zip(src_dir, zip_file_name, ignore_list=None):
    with zipfile.ZipFile(zip_file_name, 'w') as zf:
        for root, dirs, files in os.walk(src_dir):
            # Skip ignored directories
            if ignore_list:
                dirs[:] = [d for d in dirs if d not in ignore_list]
            for filename in files:
                file_path = os.path.join(root, filename)
                # Skip ignored files and directories
                if ignore_list and any(ignored in file_path for ignored in ignore_list):
                    continue
                arc_name = os.path.relpath(file_path, src_dir)
                zf.write(file_path, arcname=arc_name)


package_to_zip(
    src_dir='../backend',
    zip_file_name='CountWorker v1.2.zip',
    ignore_list=['__pycache__', 'CountWorker v1.2.zip', 'static', '.idea']
)
