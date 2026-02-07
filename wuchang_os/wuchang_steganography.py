import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add current directory to path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from memory_card import chronos_amplifier_manual_sealed
    PAYLOAD = chronos_amplifier_manual_sealed.DATA_PAYLOAD
except ImportError:
    # Fallback
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'memory_card'))
    import chronos_amplifier_manual_sealed
    PAYLOAD = chronos_amplifier_manual_sealed.DATA_PAYLOAD

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)
OUTPUT_IMAGE_PATH = os.path.join(STATIC_DIR, 'mars_secret.png')

def text_to_bits(text):
    """Convert text to a binary string."""
    bits = bin(int.from_bytes(text.encode('utf-8', 'surrogatepass'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    """Convert binary string back to text."""
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', 'surrogatepass') or '\\0'

def encode_image(payload):
    print(f"[Steganography] Encoding payload of length {len(payload)}...")
    
    # 1. Create a base image (Mars Red)
    width, height = 400, 400
    img = Image.new('RGB', (width, height), color='#561208') # Dark Mars Red
    draw = ImageDraw.Draw(img)
    
    # Add some visible "cover" text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((120, 180), "WUCHANG PROTOCOL", fill='#FF5733', font=font) # Lighter Mars Red
    draw.text((130, 200), "CLASSIFIED DATA", fill='#FF5733', font=font)
    
    # 2. Prepare payload bits
    # Add a delimiter to know when to stop reading
    full_payload = payload + "||EOF||"
    bits = text_to_bits(full_payload)
    
    pixels = img.load()
    data_idx = 0
    
    print(f"[Steganography] Total bits to hide: {len(bits)}")
    if len(bits) > width * height * 3:
        raise ValueError("Payload too large for this image size!")
        
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Modify Red channel LSB
            if data_idx < len(bits):
                r = (r & ~1) | int(bits[data_idx])
                data_idx += 1
                
            # Modify Green channel LSB
            if data_idx < len(bits):
                g = (g & ~1) | int(bits[data_idx])
                data_idx += 1
                
            # Modify Blue channel LSB
            if data_idx < len(bits):
                b = (b & ~1) | int(bits[data_idx])
                data_idx += 1
                
            pixels[x, y] = (r, g, b)
            
            if data_idx >= len(bits):
                break
        if data_idx >= len(bits):
            break
            
    img.save(OUTPUT_IMAGE_PATH)
    print(f"[Steganography] Image saved to: {OUTPUT_IMAGE_PATH}")
    return img

def decode_image(image_path):
    print(f"[Steganography] Decoding from: {image_path}...")
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    bits = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            bits += str(r & 1)
            bits += str(g & 1)
            bits += str(b & 1)
            
    # Convert bits to text until delimiter
    # This is a bit inefficient for large images but fine for demo
    # We look for the "||EOF||" pattern in binary? 
    # Or just convert chunks. Let's convert all and search string.
    
    # Optimization: Convert in chunks of 8 bits to check for chars
    decoded_text = ""
    current_byte = ""
    
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        
        char_code = int(byte, 2)
        if char_code == 0: break # Null terminator check
        
        try:
            char = chr(char_code)
            decoded_text += char
            if decoded_text.endswith("||EOF||"):
                return decoded_text[:-7] # Remove delimiter
        except:
            continue
            
    return "Decoding Failed or EOF not found"

if __name__ == "__main__":
    print(">>> WUCHANG STEGANOGRAPHY MODULE ACTIVATED <<<")
    try:
        encode_image(PAYLOAD)
        
        # Verify
        result = decode_image(OUTPUT_IMAGE_PATH)
        print("\n>>> VERIFICATION RESULT <<<")
        print(f"Original Start: {PAYLOAD[:20]}...")
        print(f"Decoded Start : {result[:20]}...")
        
        if result == PAYLOAD:
            print(">>> SUCCESS: Payload perfectly hidden and retrieved! <<<")
        else:
            print(">>> WARNING: Mismatch detected! <<<")
            
    except Exception as e:
        print(f"Error: {e}")
