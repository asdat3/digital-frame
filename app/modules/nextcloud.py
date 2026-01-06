from app.config.config import settings
from nc_py_api import Nextcloud
import random


IMAGE_EXTENSIONS = {'.webp', '.jpg', '.jpeg', '.png'}


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


def get_random_image() -> tuple[bytes, str] | None:
    """
    Get a random image from Nextcloud folder.
    
    Returns:
        Tuple of (image_bytes, content_type) or None if no images found
    """
    try:
        nc = connect_to_nextcloud()
        folder_path = settings.nextcloud_folder
        files = list_files_in_folder(nc, folder_path)
        
        # Filter for image files only
        image_files = [
            f for f in files
            if not f.is_dir and any(f.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
        ]
        
        if not image_files:
            return None
        
        # Pick a random image
        chosen_file = random.choice(image_files)
        file_path = f"{folder_path.rstrip('/')}/{chosen_file.name}"
        
        # Download the image content
        image_bytes = nc.files.download(file_path)
        
        # Determine content type
        ext = chosen_file.name.lower().split('.')[-1]
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }
        content_type = content_types.get(ext, 'image/jpeg')
        
        return image_bytes, content_type
        
    except Exception as e:
        print(f"Error getting random image: {e}")
        return None


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
