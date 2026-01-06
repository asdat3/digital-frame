"""
Nextcloud API Example - List files from a folder
Uses nc_py_api to connect to Nextcloud and retrieve files
"""

import os
from nc_py_api import Nextcloud

NEXTCLOUD_URL = "https://storage.asdatindustries.com"
NEXTCLOUD_USER = "Bot Automatisierung"
NEXTCLOUD_PASSWORD = "tRW44-QRY9Z-njNsA-s39y8-wGg4C"

def connect_to_nextcloud() -> Nextcloud:
    """Establish connection to Nextcloud instance."""
    if not NEXTCLOUD_PASSWORD:
        raise ValueError("NEXTCLOUD_PASSWORD environment variable not set")
    
    nc = Nextcloud(
        nextcloud_url=NEXTCLOUD_URL,
        nc_auth_user=NEXTCLOUD_USER,
        nc_auth_pass=NEXTCLOUD_PASSWORD,
    )
    return nc


def list_files_in_folder(nc: Nextcloud, folder_path: str = "/") -> list:
    """
    List all files and folders in a given path.
    
    Args:
        nc: Nextcloud connection instance
        folder_path: Path to the folder (default: root "/")
    
    Returns:
        List of file/folder objects
    """
    files = nc.files.listdir(folder_path)
    return files


def print_file_info(files: list) -> None:
    """Pretty print file information."""
    print(f"\n{'Name':<40} {'Type':<10} {'Size':<15} {'Modified'}")
    print("-" * 85)
    
    for file in files:
        file_type = "Folder" if file.is_dir else "File"
        size = "-" if file.is_dir else f"{file.info.size:,} bytes"
        modified = file.info.last_modified.strftime("%Y-%m-%d %H:%M") if file.info.last_modified else "-"
        
        print(f"{file.name:<40} {file_type:<10} {size:<15} {modified}")


def main():
    """Main function to demonstrate Nextcloud file listing."""
    try:
        # Connect to Nextcloud
        print(f"Connecting to {NEXTCLOUD_URL}...")
        nc = connect_to_nextcloud()
        print("✓ Connected successfully!")
        
        folder_to_list = "/Shared/Favorite/"  # Change this to any folder path you want
        print(f"\nListing files in: {folder_to_list}")
        
        files = list_files_in_folder(nc, folder_to_list)
        
        if files:
            print_file_info(files)
            print(f"\nTotal items: {len(files)}")
        else:
            print("No files found in this folder.")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
