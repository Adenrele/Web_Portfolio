import qrcode
import os

class QRCreator:
    def __init__(self, url, file_name, file_type):
        self.url = url
        self.file_name = file_name
        self.file_type = file_type
        

    def create_qr_code(self):
        """
  
        """
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,  # Controls the size of the QR Code; higher numbers mean bigger codes
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
            box_size=10,  # Size of each box in the QR code grid
            border=4,  # Border size (minimum is 4)
        )
        qr.add_data(self.url)
        qr.make(fit=True)

        # Create an image of the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        return img

    def save_qr(self, img):
        folder = "static/QR"
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, self.file_name + "." + self.file_type)
        img.save(file_path)
        return os.path.join("QR", self.file_name + "." + self.file_type)

#Example usage
test = QRCreator(url="unzippd.co.uk", file_name="unzippd", file_type="png")
qr_image = test.create_qr_code()
file_name = test.save_qr(qr_image)