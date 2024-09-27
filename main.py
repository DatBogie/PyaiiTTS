import sys, json, os
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QComboBox, QTextEdit, QFrame, QColorDialog, QInputDialog, QDoubleSpinBox, QSlider
from PyQt6.QtCore import Qt, pyqtSignal
from functools import partial
from elevenlabs.client import ElevenLabs
from random import randrange
import requests
from elevenlabs import VoiceSettings

__start__ = False

root = "/"
s = "/"
if sys.platform == "win32":
    s = "\\"
    root = "C:\\"

class RGB():
    def __init__(self,r:int|QColor|list[int,int,int]|tuple[int,int,int]=-1,g:int=0,b:int=0):
        if type(r) == int:
            self.r = self.clamp_num(r,0,255)
            self.g = self.clamp_num(g,0,255)
            self.b = self.clamp_num(b,0,255)
        elif type(r) == QColor:
            self.r = r.red()
            self.g = r.green()
            self.b = r.blue()
        elif type(r) == list or type(r) == tuple:
            self.r = r[0]
            self.g = r[1]
            self.b = r[2]
    def clamp_num(self,x:int,min:int,max:int):
        return x if (x >= min and x <= max) else (min if x < min else max)
    def clampTo(self,x):
        return RGB(self.clamp_num(self.r,0,x.r),self.clamp_num(self.g,0,x.g),self.clamp_num(self.b,0,x.b))

    def invert(self):
        return RGB(255-self.r,255-self.g,255-self.b)
    def add(self,x:int):
        return RGB((self.r+x),(self.g+x),((self.b+x)))
    def get(self):
        return [self.r,self.g,self.b]
    def set(self,x):
        self.r = x.r,
        self.g = x.g,
        self.b = x.b
    def lightness(self):
        return self.QColor().toHsl().lightness()
    def QColor(self):
        return QColor.fromRgb(self.r,self.g,self.b)


THEME_CHANGED = False

VOICES = {}

SYSTEM_THEME = "System (Requires Restart)"
PROTECTED_THEMES = ["Dark","Light",SYSTEM_THEME]

DEFAULT_VOICES = {
    "John": "fTt87DbpNDYfGLhYRaCj",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Wheatly": "wbkTEiY2duHYPGxRIrMb",
    "Heavy": "NXdARWuv0JFJUqSTb4RI"
}

DEFAULT_THEMES = {
    "Dark": {
        "Button": RGB(45,45,45).get(),
        "Text Input": RGB(35,35,35).get(),
        "Background": RGB(25,25,25).get(),
        "Accent": RGB(21,106,175).get()
    },

    "Light": {
        "Button": RGB(210,210,210).get(),
        "Text Input": RGB(220,220,220).get(),
        "Background": RGB(230,230,230).get(),
        "Accent": RGB(155,205,255).get()
    },

    SYSTEM_THEME: {
        "Button": RGB(0,0,0).get(),
        "Text Input": RGB(0,0,0).get(),
        "Background": RGB(0,0,0).get(),
        "Accent": RGB(0,0,0).get()
    }
}

DEFAULT_CONF = {
    "output_path": root + ("\\" if sys.platform == "win32" else ""),
    "voice_id": "",
    "text": "",
    "output_name": "",
    "voice_stability": 0.75,
    "voice_similarity": 0.75,
    "voice_model": ["eleven_monolingual_v1", "Eleven English v1"]
}

DEFAULT_PREF = {
    "Theme": "Dark"
}


if not os.path.exists("voices.json"):
    with open("voices.json","w") as f:
        json.dump(DEFAULT_VOICES,f)
        # f.write('{"John": "fTt87DbpNDYfGLhYRaCj", "Adam": "pNInz6obpgDQGcFmaJgB", "Wheatly": "wbkTEiY2duHYPGxRIrMb", "Heavy": "NXdARWuv0JFJUqSTb4RI"}')
with open("voices.json","r") as f:
    try:
        VOICES = json.load(f)
    except:
        VOICES = DEFAULT_VOICES
        try:
            os.rename("voices.json","voices (backup).json")
        except:pass
        with open("voices.json","w") as f:
            json.dump(DEFAULT_VOICES,f)


# VOICES = {
#     "John": "fTt87DbpNDYfGLhYRaCj",
#     "Adam": "pNInz6obpgDQGcFmaJgB",
#     "Wheatly": "wbkTEiY2duHYPGxRIrMb",
#     "Heavy": "NXdARWuv0JFJUqSTb4RI"
# }

# print(RGB(255,0,0))

COLORS = {
    "Button": RGB(45,45,45), # buttons, etc
    "Text Input": RGB(35,35,35), # text inputs, etc
    "Background": RGB(25,25,25), # backgrounds/misc
    "Accent": RGB(255,255,255)
}


if not os.path.exists("themes.json"):
    with open("themes.json","w") as f:
        json.dump(DEFAULT_THEMES,f)

with open("themes.json","r") as f:
    try:
        _themes = json.load(f)
        for k, v in DEFAULT_THEMES.items():
            _themes[k] = v
    except:
        _themes = DEFAULT_THEMES
    THEMES:dict = _themes
for n,t in THEMES.items():
    for nc,c in t.items():
        THEMES[n][nc] = RGB(c)


def s0(c:str): # Background
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QWidget { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"
def s1(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QPushButton, QComboBox, QDoubleSpinBox { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"
def s2(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QLineEdit, QTextEdit { "+f'background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); color: {z};'+" }"
def s3(c:str):
    # z="white"
    # if COLORS[c].lightness() >= 128:
    #     z="black"
    return "QWidget { "+f'selection-background-color: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b});'+" }" + "QSlider::handle::horizontal { "+f'background: rgb({COLORS[c].r},{COLORS[c].g},{COLORS[c].b}); border-radius: 4px;'+" }"

COLOR_FUNCTIONS = {
    "Background": s0,
    "Button": s1,
    "Text Input": s2,
    "Accent": s3
}

class QDoubleSpinBoxLabelSlider(QDoubleSpinBox):
    anyValueChanged = pyqtSignal(float)
    def __init__(self,text:str,min:float|None=None,max:float|None=None):
        super().__init__()
        self.QLabel = QLabel(text)
        self.QSlider = QSlider(Qt.Orientation.Horizontal)
        if min!=None and max!=None:
            self.setRange(min,max)
            self.QSlider.setRange(min,max*100)
        self.QHBoxLayout = QHBoxLayout()
        self.QHBoxLayout.addWidget(self,1)
        self.QHBoxLayout.addWidget(self.QSlider,10)
        self.QLayout = QVBoxLayout()
        self.QLayout.addWidget(self.QLabel)
        self.QLayout.addLayout(self.QHBoxLayout)
        
        self.QSlider.valueChanged.connect(self.slider_move)
        self.valueChanged.connect(self.spin_change)
    def slider_move(self):
        self.setValue(self.QSlider.value()/100)
        self.value_changed()
    def spin_change(self):
        self.QSlider.setValue(int(self.value()*100))
        self.value_changed()
    def value_changed(self):
        self.anyValueChanged.emit(self.value())
    def anySetValue(self,val:float):
        self.setValue(val)
        self.QSlider.setValue(int(val*100))

class MainWindow(QWidget):
    def __init__(self):
        global __start__
        super().__init__()

        if __start__ == False:
            __start__ = True
            if os.path.exists("key.txt"):
                with open("key.txt","r") as f:
                    key = f.read().strip()
                req = requests.get("https://api.elevenlabs.io/v1/voices",headers={"xi-api-key": key})
                if req.status_code == 200:
                    self.key = key
                else:
                    x = QMessageBox.critical(self,"PyaiiTTS | Get API Key","Invalid API key found in key.txt.\nPlease enter a valid key into key.txt and relaunch.",QMessageBox.StandardButton.Ok)
                    self.close()
                    sys.exit()
            else:
                key, s = QInputDialog.getText(self,"PyaiiTTS | Get API Key","Please enter your elevenlabs.io API key.")
                if not s:
                    raise Exception("Please paste your elevenlabs.io key into key.txt")
                req = requests.get("https://api.elevenlabs.io/v1/voices",headers={"xi-api-key": key})
                if req.status_code == 200:
                    self.key = key
                    with open("key.txt","w") as f:
                        f.write(key)
                else:
                    x = QMessageBox.critical(self,"PyaiiTTS | Get API Key","Invalid API key.\nPlease relaunch and try again.",QMessageBox.StandardButton.Ok)
                    self.close()
                    sys.exit()
            if not os.path.exists("conf.json"):
                with open("conf.json","w") as f:
                    json.dump(DEFAULT_CONF,f)
                    # f.write('{\n\t"output_path": "'+root+ ("\\" if sys.platform == "win32" else "") +'",\n\t"voice_id": "",\n\t"text": "",\n\t"output_name": "output"\n}')

            with open("conf.json","r") as f:
                try:
                    data = json.load(f)
                except:
                    data = DEFAULT_CONF
            self.data = data

            if not os.path.exists("pref.json"):
                with open("pref.json","w") as f:
                    json.dump(DEFAULT_PREF,f)
            with open("pref.json","r") as f:
                try:
                    prefer = json.load(f)
                except:
                    prefer = DEFAULT_PREF
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

        model_label = QLabel("AI Voice Model:")
        self.model = QComboBox()
        self.model.activated.connect(self.change_model)
        
        self.voice_settings = QComboBox()
        self.stability = QDoubleSpinBoxLabelSlider("AI Stability",0,1)
        self.stability.QLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stability.anySetValue(self.data["voice_stability"])
        self.stability.anyValueChanged.connect(partial(self.set_voice_settings,0))
        self.similarity = QDoubleSpinBoxLabelSlider("AI Similarity",0,1)
        self.similarity.anySetValue(self.data["voice_similarity"])
        self.similarity.QLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.similarity.anyValueChanged.connect(partial(self.set_voice_settings,1))

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

        self.pref_cl = QLabel("Colors:")
        self.pref_cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pref_c = {}

        pref_layout = QVBoxLayout()
        pref_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.pref_layout = QVBoxLayout()
        self.pref_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.addWidgets(pref_layout,[pref_l,self.pref_tl,self.pref_t,self.pref_cl])

        pref_layout.addLayout(self.pref_layout)

        self.pref_t_save = QPushButton("Save theme as...")
        self.pref_t_save.clicked.connect(self.save_theme)

        self.pref_t_remove = QPushButton("Remove Theme...")
        self.pref_t_remove.clicked.connect(self.remove_theme)

        self.pref_reset = QPushButton("⚠️ Reset Everything ⚠️")
        self.pref_reset.clicked.connect(self.reset)

        self.addWidgets(pref_layout,[self.pref_t_save,self.pref_t_remove,self.pref_reset])

        self.pref.setLayout(pref_layout)

        self.pref_btn.clicked.connect(self.show_pref)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.run_btn)
        btns_layout.addWidget(self.save_btn)
        btns_layout.addWidget(self.save_p_btn)
        btns_layout.addWidget(self.pref_btn)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.addWidgets(layout,[l,input_label,self.text_input,voice_label,self.voice,output_name_label,self.output_input,output_label,self.output,model_label,self.model])
        layout.addLayout(self.stability.QLayout)
        layout.addLayout(self.similarity.QLayout)
        layout.addLayout(btns_layout)
        self.setLayout(layout)

        for n in COLORS.keys():
            self.pref_c[n] = QPushButton(f"Change {n} Color")
            self.pref_c[n].clicked.connect(partial(self.change_c,n))
            self.pref_layout.addWidget(self.pref_c[n])

        self.pref_t.addItems(THEMES.keys())

        try:
            self.apply_theme(self.prefer["Theme"])
        except:
            self.prefer["Theme"] = list(THEMES.keys())[0]
            self.apply_theme(self.prefer["Theme"])
        self.set_style()
        # self.setStyleSheet(self.get_style())

        try:
            self.pref_t.setCurrentIndex(
                list(THEMES.keys()).index(self.prefer["Theme"])
            )
        except:pass

        self.MODELS = []
        req = requests.get("https://api.elevenlabs.io/v1/models",headers={"xi-api-key": self.key, "Content-Type": "application/json"})
        for x in req.json():
            if x["can_do_text_to_speech"]:
                self.MODELS.append([x["model_id"],x["name"]])
                self.model.addItem(x["name"])
        self.model.setCurrentIndex(self.MODELS.index(self.data["voice_model"]))

    def set_voice_settings(self,x:int):
        if x == 0:
            self.data["voice_stability"] = self.stability.value()
        elif x == 1:
            self.data["voice_similarity"] = self.similarity.value()
    
    def change_model(self):
        self.data["voice_model"] = self.MODELS[self.model.currentIndex()]
    
    def reset(self):
        x = QMessageBox.warning(self,"PyaiiTTS | Reset All","Are you sure you want to reset EVEYRTHING?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
        if x != QMessageBox.StandardButton.Yes: return
        code = int(f"{randrange(0,10)}{randrange(0,10)}{randrange(0,10)}")
        y, s = QInputDialog.getInt(self,"PyaiiTTS | Reset All",f"Enter {code} to confirm.")
        if not s or y != code: return
        to_remove = [
            "conf.json",
            "pref.json",
            "themes.json",
            "voices.json"
        ]
        for v in to_remove:
            if os.path.exists(v):
                os.remove(v)
        z = QMessageBox.question(self,"PyaiiTTS","Quit PyaiiTTs now?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
        if z != QMessageBox.StandardButton.Yes: return
        self.close()
        sys.exit()

    def dump_THEMES(self):
        _themes = THEMES.copy()
        for k,v in _themes.items():
            for y, x in v.items():
                _themes[k][y] = x.get()
        try:
            # print(_themes)
            with open("themes.json","w") as f:
                json.dump(_themes,f)
        except Exception as e:
            return e
        for k,v in _themes.items():
            for y, x in v.items():
                _themes[k][y] = RGB(x)

    def remove_theme(self):
        name, s = QInputDialog.getText(self,"PyaiiTTS | Remove Theme","Remove theme of name:")
        if not s or name in PROTECTED_THEMES: return
        if name in list(THEMES.keys()):
            x = QMessageBox.warning(self,"PyaiiTTS | Remove Theme",f"Remove theme '{name}'?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
            if x != QMessageBox.StandardButton.Yes: return
            ind = list(THEMES.keys()).index(name)
            del THEMES[name]
            e = self.dump_THEMES()
            if e: QMessageBox.critical(self,"PyaiiTTS | Remove Theme",str(e)); return
            if self.prefer["Theme"] == name:
                print()
                self.apply_theme(list(THEMES.keys())[(ind-1 if list(THEMES.keys())[ind-1] != SYSTEM_THEME else 0) if ind > 0 else 0])
                self.pref_t.setCurrentIndex(
                    list(THEMES.keys()).index(self.prefer["Theme"])
                )
            self.pref_t.removeItem(ind)
            QMessageBox.information(self,"PyaiiTTS | Remove Theme",f"Theme '{name}' removed successfully!")
        else:
            QMessageBox.critical(self,"PyaiiTTS | Remove Theme",f"Invalid theme '{name}'!")

    def save_theme(self):
        name, s = QInputDialog.getText(self,"PyaiiTTS | Save Theme","Save Theme as:")
        if not s or name in PROTECTED_THEMES: return
        if name in list(THEMES.keys()):
            x = QMessageBox.warning(self,"PyaiiTTS | Save Theme",f"Overwrite existing theme '{name}'?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
            if x != QMessageBox.StandardButton.Yes: return
        THEMES[name] = COLORS
        self.apply_theme(name)
        e = self.dump_THEMES()
        if e: QMessageBox.critical(self,"PyaiiTTS | Save Theme",str(e)); return
        self.pref_t.addItem(name)
        self.pref_t.setCurrentIndex(
            list(THEMES.keys()).index(self.prefer["Theme"])
        )
        QMessageBox.information(self,"PyaiiTTS | Save Theme",f"Theme '{name}' saved and applied successfully!")

    def apply_current_theme(self,x:QComboBox):
        self.apply_theme(x.currentText())

    def apply_theme(self,t:str):
        global COLORS, THEME_CHANGED
        last_theme = self.prefer["Theme"]
        self.prefer["Theme"] = t
        if t == SYSTEM_THEME and THEME_CHANGED:
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
        if self.prefer["Theme"] != SYSTEM_THEME:
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
        voice_settings = VoiceSettings(stability=self.data['voice_stability'],similarity_boost=self.data['voice_similarity'])
        x=self.client.generate(text=self.data["text"],voice=self.data["voice_id"],voice_settings=voice_settings,model=self.data['voice_model'][0])
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
