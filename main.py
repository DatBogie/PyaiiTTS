import sys, json, os
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QComboBox, QTextEdit, QFrame, QColorDialog
from PyQt6.QtCore import Qt
from functools import partial
from elevenlabs.client import ElevenLabs

__start__ = False

root = "/"
s = "/"
if sys.platform == "win32":
    s = "\\"
    root = "C:\\"

THEME_CHANGED = False

VOICES = {}

if not os.path.exists("voices.json"):
    with open("voices.json","w") as f:
        json.dump({
            "John": "fTt87DbpNDYfGLhYRaCj",
            "Adam": "pNInz6obpgDQGcFmaJgB",
            "Wheatly": "wbkTEiY2duHYPGxRIrMb",
            "Heavy": "NXdARWuv0JFJUqSTb4RI"
        },f)
        # f.write('{"John": "fTt87DbpNDYfGLhYRaCj", "Adam": "pNInz6obpgDQGcFmaJgB", "Wheatly": "wbkTEiY2duHYPGxRIrMb", "Heavy": "NXdARWuv0JFJUqSTb4RI"}')
with open("voices.json","r") as f:
    VOICES = json.load(f)

# VOICES = {
#     "John": "fTt87DbpNDYfGLhYRaCj",
#     "Adam": "pNInz6obpgDQGcFmaJgB",
#     "Wheatly": "wbkTEiY2duHYPGxRIrMb",
#     "Heavy": "NXdARWuv0JFJUqSTb4RI"
# }

class RGB():
    def __init__(self,r:int|QColor|list[int,int,int]|tuple[int,int,int]=-1,g:int=0,b:int=0):
        if type(r) == int:
            self.r = (r+255)%255
            self.g = (g+255)%255
            self.b = (b+255)%255
        elif type(r) == QColor:
            self.r = r.red()
            self.g = r.green()
            self.b = r.blue()
        elif type(r) == list or type(r) == tuple:
            self.r = r[0]
            self.g = r[1]
            self.b = r[2]
    def invert(self):
        return RGB(255-self.r,255-self.g,255-self.b)
    def add(self,x:int):
        return RGB(((self.r+x)+255)%255,((self.g+x)+255)%255,((self.b+x)+255)%255)
    def get(self):
        return [self.r,self.g,self.b]
    def lightness(self):
        return self.QColor().toHsl().lightness()
    def QColor(self):
        return QColor.fromRgb(self.r,self.g,self.b)

COLORS = {
    "Button": RGB(45,45,45), # buttons, etc
    "Text Input": RGB(35,35,35), # text inputs, etc
    "Background": RGB(25,25,25) # backgrounds/misc
}

if not os.path.exists("themes.json"):
    with open("themes.json","w") as f:
        json.dump({
            "Dark": {
                "Button": RGB(45,45,45).get(),
                "Text Input": RGB(35,35,35).get(),
                "Background": RGB(25,25,25).get()
            },

            "Light": {
                "Button": RGB(210,210,210).get(),
                "Text Input": RGB(220,220,220).get(),
                "Background": RGB(230,230,230).get()
            },

            "System (Requires Restart)": {
                "Button": RGB(0,0,0).get(),
                "Text Input": RGB(0,0,0).get(),
                "Background": RGB(0,0,0).get()
            }
        },f)

with open("themes.json","r") as f:
    THEMES:dict = json.load(f)
for n,t in THEMES.items():
    for nc,c in t.items():
        THEMES[n][nc] = RGB(c)


def s0(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QPushButton, QComboBox { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"
def s1(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QLineEdit, QTextEdit { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"
def s2(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QWidget { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"

COLOR_FUNCTIONS = {
    "Button": s0,
    "Text Input": s1,
    "Background": s2 
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
                with open("conf.json","w") as f:
                    json.dump({
                        "output_path": root + ("\\" if sys.platform == "win32" else ""),
                        "voice_id": "",
                        "text": "",
                        "output_name": ""
                    },f)
                    # f.write('{\n\t"output_path": "'+root+ ("\\" if sys.platform == "win32" else "") +'",\n\t"voice_id": "",\n\t"text": "",\n\t"output_name": "output"\n}')

            with open("conf.json","r") as f:
                data = json.load(f)
            self.data = data

            if not os.path.exists("pref.json"):
                with open("pref.json","w") as f:
                    json.dump({
                        "Theme": "Dark"
                    },f)
            with open("pref.json","r") as f:
                prefer = json.load(f)
            self.prefer = prefer

            self.client = ElevenLabs(
                api_key=self.key
            )

        self.setWindowTitle("PyaiiTTS")
        self.setMinimumSize(800,600)

        l = QLabel("PyaiiTTS")
        l.setStyleSheet("font-size: 12pt;")
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_label = QLabel("Text:")

        self.text_input = QTextEdit(self.data["text"])
        self.text_input.setPlaceholderText("Enter the text to be spoken here...")
        self.text_input.setToolTip("Put the text you want the AI voice to say here.")

        voice_label = QLabel("Voice:")

        self.voice = QComboBox()
        self.voice.addItems(VOICES.keys())
        try:
            self.voice.setCurrentIndex(
                list(VOICES.values()).index(self.data["voice_id"])
            )
        except:pass
        self.voice.setToolTip("Choose which voice you want the AI to speak in.\nMore voices can be added by editing the voices.json file.")

        self.voice.activated.connect(self.change_voice)

        output_name_label = QLabel("Ouput Name:")

        self.output_input = QLineEdit(self.data["output_name"])
        self.output_input.setPlaceholderText("Enter the name of the outputted file...")
        self.output_input.editingFinished.connect(self.upd_file)
        self.output_input.setToolTip("Change the name of the outputted mp3. You don't need to append a file extensions.")

        output_label = QLabel("Output:")

        self.output = QPushButton(f'Choose Output Location ({self.data["output_path"]})')
        self.output.clicked.connect(self.choose_dir)
        self.output.setStyleSheet("text-align: left;")
        self.output.setToolTip("Choose where the outputted mp3 will be located.")

        self.run_btn = QPushButton("Save and Generate")
        self.run_btn.clicked.connect(self.generate)
        self.run_btn.setToolTip("Save all configurations before attempting to generate the mp3 of the AI voice.")

        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save)
        self.save_btn.setToolTip("Save all current options to conf.json.")

        self.save_p_btn = QPushButton("Save Preferences")
        self.save_p_btn.clicked.connect(self.save_p)
        self.save_p_btn.setToolTip("Save all preferences to pref.json.")
        
        self.pref_btn = QPushButton("⚙")
        self.pref_btn.setMaximumWidth(25)
        self.pref_btn.setToolTip("Edit preferences.")
        
        self.pref = QFrame(self)
        self.pref.setWindowTitle("PyaiiTTS | Preferences")
        self.pref.setWindowFlag(Qt.WindowType.Popup, True)
        self.pref.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),self.y()+int((self.height()-(self.height()/1.1))/2),0,0)
        self.pref.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))

        pref_l = QLabel("Preferences")
        pref_l.setStyleSheet("font-size: 12pt;")
        pref_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pref_tl = QLabel("Themes:")
        self.pref_tl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pref_t = QComboBox()
        self.pref_t.setEditable(True)
        self.pref_t.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pref_t.lineEdit().setReadOnly(True)

        self.pref_t.activated.connect(partial(self.apply_current_theme,self.pref_t))

        self.pref_c = {}

        self.pref_layout = QVBoxLayout()
        self.pref_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.addWidgets(self.pref_layout,[pref_l,self.pref_tl,self.pref_t])

        self.pref.setLayout(self.pref_layout)
        
        self.pref_btn.clicked.connect(self.show_pref)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.run_btn)
        btns_layout.addWidget(self.save_btn)
        btns_layout.addWidget(self.save_p_btn)
        btns_layout.addWidget(self.pref_btn)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(l)
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

        for n in COLORS.keys():
            self.pref_c[n] = QPushButton(f"Change {n} Color")
            self.pref_c[n].clicked.connect(partial(self.change_c,n))
            self.pref_layout.addWidget(self.pref_c[n])

        self.pref_t.addItems(THEMES.keys())

        self.apply_theme(self.prefer["Theme"])
        self.set_style()
        # self.setStyleSheet(self.get_style())

        try:
            self.pref_t.setCurrentIndex(
                list(THEMES.keys()).index(self.prefer["Theme"])
            )
        except:pass

    def apply_current_theme(self,x:QComboBox):
        self.apply_theme(x.currentText())
    
    def apply_theme(self,t:str):
        global COLORS, THEME_CHANGED
        last_theme = self.prefer["Theme"]
        self.prefer["Theme"] = t
        if t == "System (Requires Restart)" and THEME_CHANGED:
            x = QMessageBox.question(self,"PyaiiTTS","Quit PyaiiTTs now?\nYour configurations and preferences will be saved.",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
            if x == QMessageBox.StandardButton.Yes:
                self.save()
                self.save_p()
                self.close()
                sys.exit()
            else:
                self.apply_theme(last_theme)
                try:
                    self.pref_t.setCurrentIndex(
                        list(THEMES.keys()).index(self.prefer["Theme"])
                    )
                except:pass
        else:
            COLORS = THEMES[t].copy()
            self.set_style()
        THEME_CHANGED = True
    
    def addWidgets(self,x:QHBoxLayout|QVBoxLayout,y:list[QWidget]):
        for v in y:
            x.addWidget(v)

    def show_pref(self):
        self.pref.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),(self.y()+int((self.height()-(self.height()/1.1))/2)),0,0)
        self.pref.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))
        self.toggle_el(self.pref)
    
    def get_style(self):
        x=""
        for n,v in COLOR_FUNCTIONS.items():
            if n != "Background":
                x+=v(n)
        return COLOR_FUNCTIONS["Background"]("Background")+x

    def set_style(self):
        if self.prefer["Theme"] != "System (Requires Restart)":
            self.setStyleSheet(self.get_style())
            for c,v in self.pref_c.items():
                z="white"
                if COLORS[c].lightness() >= 128:
                    z="black"
                v.setStyleSheet(f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};')

    def change_c(self,c:str):
        def x(y:QColor):
            COLORS[c] = RGB(y)
            self.set_style()
            # self.setStyleSheet(self.get_style())
            # z="white"
            # if COLORS[c].lightness() >= 128:
            #     z="black"
            # self.pref_c[c].setStyleSheet(f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};')
        if c in COLORS.keys():
            cd = QColorDialog(COLORS[c].QColor(),self)
            cd.show()
            cd.colorSelected.connect(x)
    
    def toggle_el(self,el):
        el.setVisible(not el.isVisible())

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
        self.save()
        x=self.client.generate(text=self.data["text"],voice=self.data["voice_id"])
        with open(f"{self.data['output_path']}{s}{self.data['output_name']}.mp3","wb") as f:
            f.write(b''.join(x))
            QMessageBox.information(self,"PyaiiTTS","TTS Success!")

    def save_p(self):
        try:
            # self.setWindowTitle("PyaiiTTS")
            # prefer = {"Theme": self.prefer["Theme"]}
            with open("pref.json","w") as f:
                json.dump(self.prefer,f)
            QMessageBox.information(self,"PyaiiTTS","Successfully Saved Preferences",QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self,str(e),QMessageBox.StandardButton.Close)
    
    def save(self):
        try:
            self.upd_text()
            self.upd_file()
            self.change_voice()
            # self.setWindowTitle("PyaiiTTS")
            # data = {"output_path": self.data["output_path"], "voice_id": self.data["voice_id"], "text": self.data["text"], "output_name": self.data["output_name"]}
            with open("conf.json","w") as f:
                json.dump(self.data,f)
            QMessageBox.information(self,"PyaiiTTS","Successfully Saved Configurations",QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self,str(e),QMessageBox.StandardButton.Close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
