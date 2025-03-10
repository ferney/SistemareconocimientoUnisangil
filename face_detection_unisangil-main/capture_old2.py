import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class CaptureImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capturar Fotos")
        self.setGeometry(100, 50, int(1920 / 2), int(1080 / 2) + 150)

        self.label_camera = QLabel(self)
        self.label_camera.setGeometry(0, 0, int(1920 / 2), int(1080 / 2))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(100)  # Actualizar la vista previa cada 100 milisegundos

        self.label_name = QLabel("Nombre Completo:", self)
        self.label_name.move(20, 560)

        self.entry_name = QLineEdit(self)
        self.entry_name.setGeometry(140, 560, 200, 30)

        self.label_dni = QLabel("CC/TI:", self)
        self.label_dni.move(20, 600)

        self.entry_dni = QLineEdit(self)
        self.entry_dni.setGeometry(140, 600, 200, 30)

        self.label_creature = QLabel("Programa Académico:", self)
        self.label_creature.move(20, 640)

        self.combo_creature = QComboBox(self)
        self.combo_creature.setGeometry(140, 640, 200, 30)
        self.load_creatures()

        self.button = QPushButton("Capturar Fotos", self)
        self.button.setGeometry(360, 560, 140, 110)
        self.button.clicked.connect(self.start_capture)

        self.cam = cv2.VideoCapture(0)

    def load_creatures(self):
        creatures = []
        if os.path.exists('data.txt'):
            with open('data.txt', encoding='utf-8') as inFile:
                creatures = [line.strip() for line in inFile]
        self.combo_creature.addItems(creatures)

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
        name = self.entry_name.text().strip() + ", " + self.entry_dni.text().strip()+ ", " + self.combo_creature.currentText().strip()
        creature = self.combo_creature.currentText()
        if name == "":
            QMessageBox.critical(self, "Error", "Por favor ingresa un nombre")
            return

        # check if name exists
        if os.path.exists("names.txt"):
            with open("names.txt", "r") as file:
                names = file.readlines()
                names = [n.strip() for n in names]
                if name in names:
                    QMessageBox.critical(self, "Error", "El nombre ya existe")
                    return

        if not os.path.exists("train_dir"):
            os.makedirs("train_dir")

        #file_count = len([entry for entry in os.listdir("train_dir") if os.path.isfile(os.path.join("train_dir", entry))]) + 1

        ret, frame = self.cam.read()
        if ret:
            
            #cv2.imwrite(f"train_dir/{file_count}_{name}.jpg", frame)
            cv2.imwrite(f"train_dir/{name}.jpg", frame)
            cv2.waitKey(1000)

            with open("names.txt", "a") as file:
                file.write(name + "\n")

            QMessageBox.information(self, "Éxito", "Foto tomada y guardada correctamente")
            self.cam.release()
            cv2.destroyAllWindows()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "No se puede acceder a la cámara")
            return

if __name__ == "__main__":
    app = QApplication([])
    ventana = CaptureImage()
    ventana.show()
    app.exec_()
