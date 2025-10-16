"""
Image handlers
"""

import base64

def image_loader(image_path: str):
    """
    """

    with open(image_path, "rb") as image_file:
        binary_image_data = image_file.read()

         # 2. Encode to Base64
        base64_encoded_image = base64.b64encode(binary_image_data)

        # 3. Decode to ASCII string
        image_send_data = base64_encoded_image.decode('ascii')

        return image_send_data