import json
import os

path = '/usr/lib/code-server/lib/vscode/product.json'

try:
    with open(path, 'r') as f:
        data = json.load(f)
    
    data['extensionsGallery'] = {
        "serviceUrl": "https://marketplace.visualstudio.com/_apis/public/gallery",
        "itemUrl": "https://marketplace.visualstudio.com/items",
        "cacheUrl": "https://vscode.blob.core.windows.net/gallery/index",
        "controlUrl": "",
        "recommendationsUrl": ""
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
    print("Successfully updated product.json")
except Exception as e:
    print(f"Error: {e}")
