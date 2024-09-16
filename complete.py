import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
from deepface import DeepFace
import os
import json
import shelve
import subprocess  # Add this line to import the subprocess module

class FileLockerUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Locker with DeepFace")
        self.setGeometry(100, 100, 640, 480)

        self.camera_display = QtWidgets.QLabel(self)
        self.camera_display.setGeometry(QtCore.QRect(10, 10, 420, 340))

        self.capture_btn = QtWidgets.QPushButton("Capture Image", self)
        self.capture_btn.setGeometry(QtCore.QRect(10, 330, 120, 30))
        self.capture_btn.clicked.connect(self.capture_image)

        self.lock_btn = QtWidgets.QPushButton("Lock File", self)
        self.lock_btn.setGeometry(QtCore.QRect(140, 330, 120, 30))
        self.lock_btn.clicked.connect(self.lock_file)

        self.unlock_btn = QtWidgets.QPushButton("Unlock File", self)
        self.unlock_btn.setGeometry(QtCore.QRect(270, 330, 120, 30))
        self.unlock_btn.clicked.connect(self.unlock_file)

        self.file_path_label = QtWidgets.QLabel("Enter File Path:", self)
        self.file_path_label.setGeometry(QtCore.QRect(10, 360, 120, 30))

        self.file_path_edit = QtWidgets.QLineEdit(self)
        self.file_path_edit.setGeometry(QtCore.QRect(130, 360, 500, 30))

        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            self.camera_display.setPixmap(pix)

    def capture_image(self):
        ret, frame = self.cam.read()
        if ret:
            cv2.imwrite("captured_image.jpg", frame)

    def lock_file(self):
        file_path = self.file_path_edit.text()
        if file_path:
            status = lock(file_path)
            if status == "locked":
                QtWidgets.QMessageBox.information(self, "File Locked", "File has been locked successfully!")
            else:
                QtWidgets.QMessageBox.warning(self, "Lock Failed", "Failed to lock the file. Please check the file path.")
        else:
            QtWidgets.QMessageBox.warning(self, "Lock Failed", "Please enter the file path.")

    def unlock_file(self):
        ret, frame = self.cam.read()
        if ret:
            cv2.imwrite("verification_image.jpg", frame)
            reference_image_path = "captured_image.jpg"
            verification_image_path = "verification_image.jpg"
            if os.path.exists(reference_image_path) and os.path.exists(verification_image_path):
                try:
                    result = DeepFace.verify(reference_image_path, verification_image_path)
                    if result['verified']:
                        file_path = self.file_path_edit.text()
                        if file_path:
                            status = unlock(file_path)
                            if status == "unlocked":
                                QtWidgets.QMessageBox.information(self, "File Unlocked", "File has been unlocked successfully!")
                            else:
                                QtWidgets.QMessageBox.warning(self, "Unlock Failed", "Failed to unlock the file. Please check the file path.")
                        else:
                            QtWidgets.QMessageBox.warning(self, "Unlock Failed", "Please enter the file path.")
                    else:
                        QtWidgets.QMessageBox.warning(self, "Face Verification Failed", "Face verification failed. Please try again.")
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
            else:
                QtWidgets.QMessageBox.warning(self, "File Missing", "Reference image or verification image is missing.")
        else:
            QtWidgets.QMessageBox.warning(self, "Camera Error", "Error capturing image from camera.")



def lock(fpath):
    command1 = 'attrib +h +s "' + fpath + '"'
    subprocess.call(command1, shell=True)
    return "locked"

def unlock(fpath):
    command1 = 'attrib -h -s "' + fpath + '"'
    subprocess.call(command1, shell=True)
    return "unlocked"

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = FileLockerUI()
    win.show()
    sys.exit(app.exec_())
