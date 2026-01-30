import os
import yaml
import json
import base64
import shutil

DIST_DIR = "dist"
OUTPUT_FILE = os.path.join(DIST_DIR, "community-backends.yaml")

# Max logo size in bytes (100KB)
MAX_LOGO_SIZE = 100 * 1024 

def get_logo_base64(path):
    """Reads an image file and returns a base64 encoded data URI."""
    if not os.path.exists(path):
        return None
    
    # Check file size
    size = os.path.getsize(path)
    if size > MAX_LOGO_SIZE:
        print(f"  Warning: Logo {os.path.basename(path)} is too large ({size/1024:.1f}KB). Recommended max is 100KB.")
    
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            ext = os.path.splitext(path)[1].lower()
            mime_type = "image/png" # Default
            if ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".svg":
                mime_type = "image/svg+xml"
            elif ext == ".webp":
                mime_type = "image/webp"
            
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Warning: Failed to read logo {path}: {e}")
        return None

def main():
    # Clean up dist dir
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)

    backends = []
    
    root_dir = "."
    items = sorted(os.listdir(root_dir))
    
    for item in items:
        item_path = os.path.join(root_dir, item)
        
        if not os.path.isdir(item_path) or item.startswith(".") or item in ["dist", "scripts", "__pycache__"]:
            continue
            
        spec_path = os.path.join(item_path, "spec.yaml")
        if not os.path.exists(spec_path):
            continue
            
        print(f"Processing {item}...")
        
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = yaml.safe_load(f)
                
            if not spec:
                print(f"  Warning: Empty spec in {item}")
                continue

            logo_path = None
            for ext in [".png", ".jpg", ".jpeg", ".svg", ".webp"]:
                possible_path = os.path.join(item_path, f"logo{ext}")
                if os.path.exists(possible_path):
                    logo_path = possible_path
                    break
            
            if logo_path:
                logo_data = get_logo_base64(logo_path)
                if logo_data:
                    spec['icon'] = logo_data
                    print(f"  - Logo embedded ({os.path.getsize(logo_path)/1024:.1f}KB)")
            else:
                print(f"  - No logo found")

            backends.append(spec)
            
        except Exception as e:
            print(f"Error processing {item}: {e}")

    # Output YAML
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(backends, f, sort_keys=False, allow_unicode=True)
        print(f"\nSuccessfully bundled {len(backends)} backends to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing YAML output: {e}")


if __name__ == "__main__":
    main()
