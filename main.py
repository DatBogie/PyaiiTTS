import sys, json, os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QComboBox, QTextEdit
from PyQt6.QtCore import Qt
from functools import partial
from elevenlabs.client import ElevenLabs

__start__ = False

root = "/"
s = "/"
if sys.platform == "win32":
    s = "\\"
    root = "C:\\"

VOICES = {
    "John": "fTt87DbpNDYfGLhYRaCj",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Wheatly": "wbkTEiY2duHYPGxRIrMb",
    "Heavy": "NXdARWuv0JFJUqSTb4RI"
}

class MainWindow(QWidget):
    def __init__(self):
        global __start__
        super().__init__()
        
        if __start__ == False:
            __start__ = True
            if os.path.exists("key.txt"):
                with open("key.txt","r") as f:
                    self.key = f.read()
            else:
                raise Exception("Please paste your elevenlabs.io key into key.txt")
            if not os.path.exists("conf.json"):
                with open(r"conf.json","w") as f:
                    f.write('{\n\t"output_path": "'+root+ ("\\" if sys.platform == "win32" else "") +'",\n\t"voice_id": "",\n\t"text": "",\n\t"output_name": "output"\n}')
                
            with open(r"conf.json","r") as f:
                data = json.load(f)
            self.data = data
            
            self.client = ElevenLabs(
                api_key=self.key
            )

        self.setWindowTitle("TF2 AI TTS")
        self.setMinimumSize(800,600)

        input_label = QLabel("Text:")

        self.text_input = QTextEdit(self.data["text"])
        self.text_input.setPlaceholderText("Enter the text to be spoken here...")

        voice_label = QLabel("Voice:")

        self.voice = QComboBox()
        self.voice.addItems(VOICES.keys())
        try:
            self.voice.setCurrentIndex(
                list(VOICES.values()).index(self.data["voice_id"])
            )
        except:pass

        self.voice.activated.connect(self.change_voice)

        output_name_label = QLabel("Ouput Name:")

        self.output_input = QLineEdit(self.data["output_name"])
        self.output_input.setPlaceholderText("Enter the name of the outputted file...")
        self.output_input.editingFinished.connect(self.upd_file)

        output_label = QLabel("Output:")

        self.output = QPushButton(f'Choose Output Location ({self.data["output_path"]})')
        self.output.clicked.connect(self.choose_dir)
        self.output.setStyleSheet("text-align: left;")

        self.run_btn = QPushButton("Generate")
        self.run_btn.clicked.connect(self.generate)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.run_btn)
        btns_layout.addWidget(self.save_btn)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(input_label)
        layout.addWidget(self.text_input)
        layout.addWidget(voice_label)
        layout.addWidget(self.voice)
        layout.addWidget(output_name_label)
        layout.addWidget(self.output_input)
        layout.addWidget(output_label)
        layout.addWidget(self.output)
        layout.addLayout(btns_layout)
        self.setLayout(layout)

    
    def change_voice(self):
        self.data["voice_id"] = VOICES[self.voice.currentText()]
    
    def upd_file(self):
        self.data["output_name"] = self.output_input.text()
    
    def upd_text(self):
        escapes = ''.join([chr(char) for char in range(1, 32)])
        self.data["text"] = self.text_input.toPlainText().strip().translate(str.maketrans('','',escapes))
        self.text_input.setPlainText(self.data["text"])
    
    def choose_dir(self):
        dia = QFileDialog.getExistingDirectory(self,"Choose output directory...",self.data["output_path"])
        if dia:
            self.data["output_path"] = dia
            self.output.setText(f'Choose Output Location ({self.data["output_path"]})')
    
    def generate(self):
        x=self.client.generate(text=self.data["text"],voice=self.data["voice_id"])
        with open(f"{self.data['output_path']}{s}{self.data['output_name']}.mp3","wb") as f:
            f.write(b''.join(x))
            QMessageBox.information(self,"TF2 AI TTS","TTS Success!")
    
    def save(self):
        self.upd_text()
        self.upd_file()
        self.change_voice()
        self.setWindowTitle("TF2 AI TTS")
        data = {"output_path": self.data["output_path"], "voice_id": self.data["voice_id"], "text": self.data["text"], "output_name": self.data["output_name"]}
        with open(r"conf.json","w") as f:
            json.dump(data,f)
        QMessageBox.information(self,"TF2 AI TTS","Save Success",QMessageBox.StandardButton.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
