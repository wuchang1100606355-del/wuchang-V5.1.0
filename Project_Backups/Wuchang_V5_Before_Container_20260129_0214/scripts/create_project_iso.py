import os
import pycdlib
from datetime import datetime

ISO_PATH = r"C:\wuchang V5.0.0\project_files.iso"
SOURCE_DIR = r"C:\wuchang V5.0.0"

def make_iso(source_dir, iso_path):
    iso = pycdlib.PyCdlib()
    iso.new(interchange_level=4, joliet=3) # Enable Joliet for Windows compatibility

    # Add root files
    exclude = ['.git', '.venv', 'project_files.iso', 'Win11_25H2_Chinese_Traditional_x64.iso']
    
    print(f"Scanning {source_dir}...")
    
    # We need to walk the directory and add files
    # Note: pycdlib requires adding directories first, then files.
    # And ISO9660 paths must be upper case usually, but Rock Ridge / Joliet allow mixed.
    # We will use simple traversal.
    
    # Mapping of local path to iso path
    # ISO path format: /FOLDER/FILE
    
    for root, dirs, files in os.walk(source_dir):
        # Filter exclusions
        dirs[:] = [d for d in dirs if d not in exclude]
        
        rel_path = os.path.relpath(root, source_dir)
        if rel_path == '.':
            iso_dir = '/'
        else:
            iso_dir = '/' + rel_path.replace(os.sep, '/')
            # Create directory in ISO if not root
            try:
                iso.add_directory(iso_dir)
            except Exception as e:
                # Directory might already exist or parent issue
                pass

        for file in files:
            if file in exclude:
                continue
            if file.endswith('.iso'):
                continue
                
            local_file_path = os.path.join(root, file)
            iso_file_path = (iso_dir + '/' + file).replace('//', '/')
            
            try:
                iso.add_file(local_file_path, iso_path=iso_file_path)
            except Exception as e:
                print(f"Skipping {iso_file_path}: {e}")

    print(f"Writing ISO to {iso_path}...")
    iso.write(iso_path)
    iso.close()
    print("Done.")

if __name__ == "__main__":
    make_iso(SOURCE_DIR, ISO_PATH)
