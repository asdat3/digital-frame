from app.config.config import settings
from nc_py_api import Nextcloud


def connect_to_nextcloud() -> Nextcloud:
    """Establish connection to Nextcloud instance."""
    if not settings.nextcloud_password:
        raise ValueError("nextcloud_password environment variable not set")
    
    nc = Nextcloud(
        nextcloud_url=settings.nextcloud_url,
        nc_auth_user=settings.nextcloud_user,
        nc_auth_pass=settings.nextcloud_password,
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
        print(f"Connecting to {settings.nextcloud_url}...")
        nc = connect_to_nextcloud()
        print("✓ Connected successfully!")
        
        folder_to_list = settings.nextcloud_folder
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
