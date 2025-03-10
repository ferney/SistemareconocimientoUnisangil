import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt


class CaptureImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capturar Fotos")
        self.setGeometry(100, 100, int(1920 / 2), int(1080 / 2) + 80)

        self.label_camera = QLabel(self)
        self.label_camera.setGeometry(0, 0, int(1920 / 2), int(1080 / 2))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(100)  # Actualizar la vista previa cada 100 milisegundos

        self.label_name = QLabel("Nombre:", self)
        self.label_name.move(20, 560)

        self.entry_name = QLineEdit(self)
        self.entry_name.setGeometry(80, 560, 200, 30)

        self.button = QPushButton("Capturar Fotos", self)
        self.button.setGeometry(300, 560, 140, 30)
        self.button.clicked.connect(self.start_capture)

        self.cam = cv2.VideoCapture(0)

    def update_preview(self):
        ret, frame = self.cam.read()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            pixmap_resized = pixmap.scaled(int(1920 / 2), int(1080 / 2))
            self.label_camera.setPixmap(pixmap_resized)

    def start_capture(self):
        name = self.entry_name.text().strip()
        if name == "":
            QMessageBox.critical(self, "Error", "Por favor ingresa un nombre")
            return

        #check name exist or not
        if os.path.exists("names_old.txt"):
            with open("names_old.txt", "r") as file:
                names = file.readlines()
                names = [name.strip() for name in names]
                if name in names:
                    QMessageBox.critical(self, "Error", "El nombre ya existe")
                    return

        if not os.path.exists(f"db/{name}"):
            os.makedirs(f"db/{name}")

        for i in range(5):
            ret, frame = self.cam.read()
            if not ret:
                QMessageBox.critical(self, "Error", "No se puede acceder a la cámara")
                break

            cv2.imwrite(f"db/{name}/{name}_{i + 1}.jpg", frame)
            cv2.waitKey(500)

        with open("names_old.txt", "a") as file:
            file.write(name + "\n")

        QMessageBox.information(self, "Éxito", "Fotos tomadas y guardadas correctamente")
        exit()


if __name__ == "__main__":
    app = QApplication([])
    ventana = CaptureImage()
    ventana.show()
    app.exec_()
