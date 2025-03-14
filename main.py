import sys, json, os, requests, pyclip
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QComboBox, QTextEdit, QFrame, QColorDialog, QInputDialog, QDoubleSpinBox, QSlider, QStyleFactory, QErrorMessage
from PyQt6.QtCore import Qt, pyqtSignal
from functools import partial
from elevenlabs.client import ElevenLabs
from random import randrange
from elevenlabs import VoiceSettings
from openai import OpenAI

__start__ = False

DEFAULT_STYLE = "Fusion"

ROOT = "/"
if sys.platform == "win32":
    ROOT = "C:/"
if getattr(sys,"frozen",False):
    PDIR = os.path.dirname(sys.executable)+"/"
else:
    PDIR = os.path.dirname(os.path.abspath(__file__))+"/"

USER = os.path.expanduser("~")
    
def LOG(e:Exception|str):
    if not os.path.exists(PDIR+"log.txt"):
        with open(PDIR+"log.txt","w") as f:pass
    with open(PDIR+"log.txt","a") as f:
        f.write("\n"+str(e))

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

SYSTEM_THEME = "System"; LEGACY_SYSTEM_THEME = SYSTEM_THEME+" (Requires Restart)";
PROTECTED_THEMES = ["Dark","Light",SYSTEM_THEME]

DEFAULT_VOICES = {
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Aria": "9BWtsMINqrJLrRacOk9x",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Bill": "pqHfZKP75CvOlQylNhV4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Callum": "N2lVS1w4EtoT3dr4eOWO",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Charlotte": "XB0fDUnXU5powFXDhCwa",
    "Chris": "iP95p4xoKVk53GoZ742B",
    "Clyde": "2EiwWnXFnvU5JabPnv8n",
    "Daniel": "onwK4e9ZLuTAKqWW03F9",
    "Dave": "CYw3kZ02Hs0563khs1Fj",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Dorothy": "ThT5KcBeYPX3keUQqHPh",
    "Drew": "29vD33N1CtxCmqQRPOHJ",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Emily": "LcfcDJNUP1GQjkzn1xUU",
    "Eric": "cjVigY5qzO86Huf0OWal",
    "Ethan": "g5CIjZEefAph4nQFvHAz",
    "Fin": "D38z5RcWu1voky8WS1ja",
    "Freya": "jsCqWAovK2LkecY7zXl4",
    "George": "JBFqnCBsd6RMkjVDRZzb",
    "Gigi": "jBpfuIE2acCO8z3wKNLl",
    "Giovanni": "zcAOhNBS3c14rBihAFp1",
    "Glinda": "z9fAnlkpzviPz146aGWa",
    "Grace": "oWAxZDx7w5VEj9dCyTzz",
    "Harry": "SOYHLrjzK2X1ezoPC6cr",
    "James": "ZQe5CZNOzWyzPSCn5a3c",
    "Jeremy": "bVMeCyTHy58xNoL34h3p",
    "Jessica": "cgSgspJ2msm6clMCkdW9",
    "Jessie": "t0jbNlBVZ17f02VDIeMI",
    "Joseph": "TxGEqnHWrfWFTfGW9XjX",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Laura": "FGY2WhTYpPnrIDTdsKH5",
    "Liam": "TX3LPaxmHKxFdv7VOQHJ",
    "Lily": "pFZP5JQG7iQjIQuC4Bku",
    "Matilda": "XrExE9yKIg1WjnnlVkGX",
    "Michael": "flq6f7yk4E4fJM5XTYuZ",
    "Mimi": "zrHiDhphv9ZnVXBqCLjz",
    "Nicole": "piTKgcLEGmPE4e6mEKli",
    "Patrick": "ODq5zmih8GrVes37Dizd",
    "Paul": "5Q0t7uMcjvnagumLfvZi",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "River": "SAz9YHcvj6GT2YYXdXww",
    "Roger": "CwhRBWXzGAHq8TQ4Fs17",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
    "Sarah": "EXAVITQu4vr4xnSDxMaL",
    "Serena": "pMsXgVXv3BLzUgSXRplE",
    "Thomas": "GBv7mTt0atIp3Br8iCZE",
    "Will": "bIHbv24MWmeRgasZH58o"
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
    "output_path": PDIR[:-1],
    "voice_id": "",
    "text": "",
    "output_name": "output",
    "voice_stability": 0.75,
    "voice_similarity": 0.75,
    "voice_model": ["eleven_monolingual_v1", "Eleven English v1"]
}

if os.path.exists(PDIR+"output"):
    DEFAULT_CONF["output_path"] = PDIR+"output"

DEFAULT_PREF = {
    "Theme": "Dark",
    "WidgetStyle": "Default"
}


if not os.path.exists(PDIR+"voices.json"):
    with open(PDIR+"voices.json","w") as f:
        json.dump(DEFAULT_VOICES,f,indent=4)
        # f.write('{"John": "fTt87DbpNDYfGLhYRaCj", "Adam": "pNInz6obpgDQGcFmaJgB", "Wheatly": "wbkTEiY2duHYPGxRIrMb", "Heavy": "NXdARWuv0JFJUqSTb4RI"}')
with open(PDIR+"voices.json","r") as f:
    try:
        VOICES = json.load(f)
    except Exception as e:
        LOG(e)
        VOICES = DEFAULT_VOICES
        try:
            os.rename(PDIR+"voices.json","voices (backup).json")
        except Exception as e:LOG(e)
        with open(PDIR+"voices.json","w") as f:
            json.dump(DEFAULT_VOICES,f,indent=4)


# VOICES = {
#     "John": "fTt87DbpNDYfGLhYRaCj",
#     "Adam": "pNInz6obpgDQGcFmaJgB",
#     "Wheatly": "wbkTEiY2duHYPGxRIrMb",
#     "Heavy": "NXdARWuv0JFJUqSTb4RI"
# }

COLORS = {
    "Button": RGB(45,45,45), # buttons, etc
    "Text Input": RGB(35,35,35), # text inputs, etc
    "Background": RGB(25,25,25), # backgrounds/misc
    "Accent": RGB(255,255,255)
}


if not os.path.exists(PDIR+"themes.json"):
    with open(PDIR+"themes.json","w") as f:
        json.dump(DEFAULT_THEMES,f,indent=4)

with open(PDIR+"themes.json","r") as f:
    try:
        _themes = json.load(f)
        if LEGACY_SYSTEM_THEME in list(_themes.keys()):
            del _themes[LEGACY_SYSTEM_THEME]
        for k, v in DEFAULT_THEMES.items():
            _themes[k] = v
    except Exception as e:
        LOG(e)
        _themes = DEFAULT_THEMES
    THEMES:dict = _themes
for n,t in THEMES.items():
    for nc,c in t.items():
        THEMES[n][nc] = RGB(c)

def s0(c:str): # Background
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QWidget { "+f'background-color: {COLORS[c].QColor().name()}; color: {z};'+" }"
def s1(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    x = -1 if z=="black" else 1
    y = "dark" if z=="white" else "light"
    return "QPushButton, QComboBox, QDoubleSpinBox, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { padding: 2px; border-radius: 6px; "+f'border: 2px solid {COLORS[c].add(10*x).QColor().name()}; background-color: {COLORS[c].QColor().name()}; color: {z};'+" }" + """
QPushButton:hover, QComboBox:hover, QDoubleSpinBox:hover, QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover { """+f'border: 2px solid {COLORS["Accent"].QColor().name()}; background-color: {COLORS[c].add(15).QColor().name()}'+" }" + """
QPushButton:pressed, QComboBox:pressed, QDoubleSpinBox:pressed, QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed  { """+f'background-color: {COLORS[c].add(-10).QColor().name()};'+" }" + """
QComboBox::drop-down { background: transparent; }""" + "QComboBox::down-arrow { "+f'width: 15%; height: 15%; image: url({PDIR}assets/QComboBox-arrow-image-{y}.png);'+" }" + """
QDoubleSpinBox::up-arrow { """+f'width: 15%; height: 15%; image: url({PDIR}assets/QComboBox-arrow-up-{y}.png);'+" }" + "QDoubleSpinBox::down-arrow { "+f'width: 15%; height: 15%; image: url({PDIR}assets/QComboBox-arrow-image-{y}.png);'+" }"

def s2(c:str):
    z="white"
    if COLORS[c].lightness() >= 128:
        z="black"
    return "QLineEdit, QTextEdit { "+f'background-color: {COLORS[c].QColor().name()}; color: {z};'+" }"
def s3(c:str):
    # z="white"
    # if COLORS[c].lightness() >= 128:
    #     z="black"
    return "QWidget { "+f'selection-background-color: {COLORS[c].QColor().name()};'+" }" + "QSlider::handle:horizontal { "+f'background: {COLORS[c].QColor().name()};'+" }" + "QSlider::sub-page:horizontal { "+f'background: {COLORS[c].QColor().name()}'+" }" + "QSlider::add-page:horizontal { "+f'background: {COLORS["Button"].QColor().name()};'+" }"

COLOR_FUNCTIONS = {
    "Background": s0,
    "Button": s1,
    "Text Input": s2,
    "Accent": s3
}

class QDoubleSpinBoxLabelSlider(QDoubleSpinBox):
    anyValueChanged = pyqtSignal(float)
    def __init__(self,text:str,min:float=None,max:float=None,step:float=None):
        super().__init__()
        self.QLabel = QLabel(text)
        self.QSlider = QSlider(Qt.Orientation.Horizontal)
        if min != None and max != None:
            self.setRange(min,max)
            self.QSlider.setRange(min,(max*100)+1)
        self.QHBoxLayout = QHBoxLayout()
        self.QHBoxLayout.addWidget(self,1)
        self.QHBoxLayout.addWidget(self.QSlider,10)
        self.QLayout = QVBoxLayout()
        self.QLayout.addWidget(self.QLabel)
        self.QLayout.addLayout(self.QHBoxLayout)
        
        if not step:
            self.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        else:
            self.setSingleStep(step)
        
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

class QTextEditWrap(QTextEdit):
    def __init__(self,text:str=None):
        super().__init__(text)
    #     self.installEventFilter(self)
    # def eventFilter(self,source,event):
    #     if source == self and event.type() == QEvent.Type.KeyPress:
    #         if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
    #             return True
    #     return super().eventFilter(source, event)

class HLine(QFrame):
    def __init__(self,space:int|None=None):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        # self.setFrameShadow(QFrame.Shadow.Sunken)
        if space: self.setFixedHeight(space)

class VLine(QFrame):
    def __init__(self,space:int|None=None):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        # self.setFrameShadow(QFrame.Shadow.Sunken)
        if space: self.setFixedHeight(space)

class MainWindow(QWidget):
    def __init__(self):
        global __start__
        super().__init__()
        
        self.ComboBoxes = []
        self.IconButtons = []#QIcon(PDIR+"assets/save-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),

        if __start__ == False:
            __start__ = True
            if os.path.exists(PDIR+"key.txt"):
                with open(PDIR+"key.txt","r") as f:
                    key = f.read().strip()
                req = requests.get("https://api.elevenlabs.io/v1/voices",headers={"xi-api-key": key})
                if req.status_code == 200:
                    self.key = key
                else:
                    LOG("Invalid API key in key.txt.")
                    x = QMessageBox.critical(self,"PyaiiTTS | Get API Key","Invalid API key found in key.txt.\nPlease enter a valid key into key.txt and relaunch.",QMessageBox.StandardButton.Ok)
                    self.close()
                    sys.exit()
            else:
                key, s = QInputDialog.getText(self,"PyaiiTTS | Get API Key","Please enter your elevenlabs.io API key.")
                if not s:
                    LOG("User failed to provide key.")
                    raise Exception("Please paste your elevenlabs.io key into key.txt")
                req = requests.get("https://api.elevenlabs.io/v1/voices",headers={"xi-api-key": key})
                if req.status_code == 200:
                    self.key = key
                    with open(PDIR+"key.txt","w") as f:
                        f.write(key)
                else:
                    LOG("User entered invalid API key.")
                    x = QMessageBox.critical(self,"PyaiiTTS | Get API Key","Invalid API key.\nPlease relaunch and try again.",QMessageBox.StandardButton.Ok)
                    self.close()
                    sys.exit()
            if not os.path.exists(PDIR+"conf.json"):
                with open(PDIR+"conf.json","w") as f:
                    json.dump(DEFAULT_CONF,f,indent=4)

            with open(PDIR+"conf.json","r") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    LOG(e)
                    data = DEFAULT_CONF
            self.data = data

            if not os.path.exists(PDIR+"pref.json"):
                with open(PDIR+"pref.json","w") as f:
                    json.dump(DEFAULT_PREF,f,indent=4)
            with open(PDIR+"pref.json","r") as f:
                try:
                    prefer = json.load(f)
                except Exception as e:
                    LOG(e)
                    prefer = DEFAULT_PREF
            self.prefer = prefer

            self.client = ElevenLabs(
                api_key=self.key
            )
        
        global DEFAULT_STYLE
        DEFAULT_STYLE = app.style().name()
        
        if self.prefer["WidgetStyle"] and (self.prefer["WidgetStyle"] in QStyleFactory.keys() or self.prefer["WidgetStyle"] in ["Default","System"]):
            style = prefer["WidgetStyle"] if not self.prefer["WidgetStyle"] in ["Default","System"] else (DEFAULT_STYLE if self.prefer["WidgetStyle"] == "System" else "Fusion")
            app.setStyle(style)
        else:
            app.setStyle("Fusion")
        # if ((not "NativeWidgets" in self.prefer) and (not DEFAULT_PREF["NativeWidgets"])) or (not self.prefer["NativeWidgets"]):
        #     global DEFAULT_STYLE
        #     DEFAULT_STYLE = app.style().name()
        #     app.setStyle("fusion")

        self.setWindowTitle("PyaiiTTS")
        self.setMinimumSize(800,600)

        l = QLabel("<b>PyaiiTTS</b>")
        l.setStyleSheet("font-size: 14pt;")
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_label = QLabel("Text:")

        self.text_input = QTextEditWrap()
        self.text_input.setPlainText(self.data["text"].encode('utf-8').decode('unicode_escape'))
        self.text_input.setPlaceholderText("Enter the text to be spoken here…")
        self.text_input.setToolTip("Put the text you want the AI voice to say here.")
        
        open_gpt = QPushButton(QIcon(PDIR+"assets/chat-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Generate Text…")
        self.IconButtons.append({"icon_path":"assets/chat-","button":open_gpt})

        voice_label = QLabel("Voice:")

        self.voice = ComboBox(self)
        # self.voice.view().parentWidget().setStyleSheet("background-color: white;")
        self.voice.addItems(VOICES.keys())
        try:
            self.voice.setCurrentIndex(
                list(VOICES.values()).index(self.data["voice_id"])
            )
        except Exception as e:LOG(e)
        self.voice.setToolTip("Choose which voice you want the AI to speak in.\nMore voices can be added by editing the voices.json file.")
        self.voice.activated.connect(self.change_voice)

        self.output_name_label = QLabel("Output Name:")
        self.output_name_icon = QLabel()
        pm=QPixmap(f"{PDIR}assets/warning-{("light" if COLORS["Button"].lightness() >= 128 else "dark")}.png")
        self.output_name_icon.setPixmap(pm.scaledToWidth(16))
        self.output_name_icon.setFixedSize(16,16)
        self.output_name_icon.setToolTip(f"WARNING: File {self.data["output_path"]}/{self.data["output_name"]}.mp3 already exists!\nGenerating will overwrite this file.")
        output_name_label_layout = QHBoxLayout()
        output_name_label_layout.addWidget(self.output_name_icon)
        output_name_label_layout.addWidget(self.output_name_label)
        self.output_name_icon.setVisible(False)
        

        self.output_input = QLineEdit(self.data["output_name"])
        self.output_input.setPlaceholderText("Enter the name of the outputted file…")
        self.output_input.textChanged.connect(self.upd_file)
        self.output_input.setToolTip("Change the name of the outputted mp3. You don't need to append a file extensions.")

        output_label = QLabel("Output:")

        self.output = QPushButton(f'Choose Output Location ({self.data["output_path"]})')
        self.output.clicked.connect(self.choose_dir)
        self.output.setStyleSheet("text-align: left;")
        self.output.setToolTip("Choose where the outputted mp3 will be located.")

        model_label = QLabel("AI Voice Model:")
        self.model = ComboBox(self)
        self.model.activated.connect(self.change_model)
        
        self.voice_settings = ComboBox(self)
        self.stability = QDoubleSpinBoxLabelSlider("AI Stability",0,1)
        self.stability.QLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stability.anySetValue(self.data["voice_stability"])
        self.stability.anyValueChanged.connect(partial(self.set_voice_settings,0))
        self.similarity = QDoubleSpinBoxLabelSlider("AI Similarity",0,1)
        self.similarity.anySetValue(self.data["voice_similarity"])
        self.similarity.QLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.similarity.anyValueChanged.connect(partial(self.set_voice_settings,1))

        self.run_btn = QPushButton(QIcon(PDIR+"assets/send-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Save and Generate")
        self.run_btn.clicked.connect(self.generate)
        self.run_btn.setToolTip("Save all configurations before attempting to generate the mp3 of the AI voice.")
        self.IconButtons.append({"icon_path":"assets/send-","button":self.run_btn})

        self.save_btn = QPushButton(QIcon(PDIR+"assets/save-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Save Configuration")
        self.save_btn.clicked.connect(self.save)
        self.save_btn.setToolTip("Save all current options to conf.json.")
        self.IconButtons.append({"icon_path":"assets/save-","button":self.save_btn})

        self.save_p_btn = QPushButton(QIcon(PDIR+"assets/save-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Save Preferences")
        self.save_p_btn.clicked.connect(self.save_p)
        self.save_p_btn.setToolTip("Save all preferences to pref.json.")
        self.IconButtons.append({"icon_path":"assets/save-","button":self.save_p_btn})

        self.pref_btn = QPushButton(icon=QIcon(PDIR+"assets/settings-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")))
        self.pref_btn.setMaximumWidth(25)
        self.pref_btn.setToolTip("Edit preferences.")
        self.IconButtons.append({"icon_path":"assets/settings-","button":self.pref_btn})
        

        # Preferences

        self.pref = QWidget(self)
        self.pref.setWindowTitle("PyaiiTTS | Preferences")
        self.pref.setWindowFlag(Qt.WindowType.Popup, True)
        self.pref.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),self.y()+int((self.height()-(self.height()/1.1))/2),0,0)
        self.pref.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))

        pref_l = QLabel("<b>Preferences</b>")
        pref_l.setStyleSheet("font-size: 14pt;")
        pref_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pref_tl = QLabel("Themes")
        pref_tl.setStyleSheet("font-size: 11pt;")
        pref_tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pref_t_layout = QHBoxLayout()

        pref_t_label = QLabel("Theme:  ")
        pref_t_layout.addWidget(pref_t_label)

        self.pref_t = ComboBox(self)
        pref_t_layout.addWidget(self.pref_t,4)

        self.pref_t.activated.connect(partial(self.apply_current_theme,self.pref_t))
        
        pref_widget_style_layout = QHBoxLayout()
        
        pref_widget_style_label = QLabel("Widgets:")
        pref_widget_style_layout.addWidget(pref_widget_style_label)
        
        self.pref_widget_style = ComboBox(self)
        styles = ["Default","System"]+QStyleFactory.keys()
        self.pref_widget_style.addItems(styles)
        self.pref_widget_style.setCurrentIndex(styles.index(self.prefer["WidgetStyle"]))
        self.pref_widget_style.currentIndexChanged.connect(self.update_widget_style)
        pref_widget_style_layout.addWidget(self.pref_widget_style,4)

        pref_cl = QLabel("Colors")
        pref_cl.setStyleSheet("font-size: 11pt;")
        pref_cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pref_c = {}

        pref_layout = QVBoxLayout()
        pref_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.pref_layout = QVBoxLayout()
        self.pref_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        pref_t_save = QPushButton(QIcon(PDIR+"assets/save-as-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Save theme as…")
        pref_t_save.clicked.connect(self.save_theme)
        self.IconButtons.append({"icon_path":"assets/save-as-","button":pref_t_save})

        pref_t_remove = QPushButton(QIcon(PDIR+"assets/delete-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Remove Theme…")
        pref_t_remove.clicked.connect(self.remove_theme)
        self.IconButtons.append({"icon_path":"assets/delete-","button":pref_t_remove})
        
        pref_t_import = QPushButton(QIcon(PDIR+"assets/import-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Import theme…")
        pref_t_import.clicked.connect(self.import_theme)
        self.IconButtons.append({"icon_path":"assets/import-","button":pref_t_import})
        
        pref_t_export = QPushButton(QIcon(PDIR+"assets/export-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Export theme…")
        pref_t_export.clicked.connect(self.export_theme)
        self.IconButtons.append({"icon_path":"assets/export-","button":pref_t_export})

        self.addWidgets(pref_layout,[pref_l,pref_tl,pref_t_layout,pref_widget_style_layout,pref_t_save,pref_t_export,pref_t_import,pref_t_remove,HLine(40),pref_cl])

        pref_layout.addLayout(self.pref_layout)
        
        # self.pref_native = QCheckBox("Use Native Widget Style*")
        # self.pref_native.setToolTip("Skip forcing the app to use the Fusion style.\n*(Requires Restart)")
        # if self.prefer["NativeWidgets"]:
        #     self.pref_native.setChecked(self.prefer["NativeWidgets"])
        # else:
        #     self.pref_native.setChecked(DEFAULT_PREF["NativeWidgets"])
        # self.pref_native.checkStateChanged.connect(self.toggle_native)
        # if DEFAULT_STYLE == "fusion": self.pref_native.setDisabled(True)
        
        pref_open_p_dir = QPushButton(QIcon(PDIR+"assets/open-folder-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Open Program Directory")
        pref_open_p_dir.clicked.connect(self.open_prg_dir)
        self.IconButtons.append({"icon_path":"assets/open-folder-","button":pref_open_p_dir})

        self.pref_reset = QPushButton(QIcon(PDIR+"assets/warning-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Reset Everything")
        self.pref_reset.clicked.connect(self.reset)
        self.IconButtons.append({"icon_path":"assets/warning-","button":self.pref_reset})

        pref_other = QLabel("Other")
        pref_other.setStyleSheet("font-size: 11pt;")
        pref_other.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.addWidgets(pref_layout,[HLine(40),pref_other,pref_open_p_dir,self.pref_reset])

        self.pref.setLayout(pref_layout)

        self.pref_btn.clicked.connect(self.show_pref)
        
        # GPT
        
        self.gpt = QWidget(self)
        self.gpt.setWindowTitle("PyaiiTTS | Generate Text")
        self.gpt.setWindowFlag(Qt.WindowType.Popup, True)
        self.gpt.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),self.y()+int((self.height()-(self.height()/1.1))/2),0,0)
        self.gpt.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))
        
        oai_key = ""   
        try:
            if not os.path.exists(PDIR+"openai-key.txt"):
                with open(PDIR+"openai-key.txt","w") as f:f.write("")
            with open(PDIR+"openai-key.txt","r") as f:
                oai_key = f.read().strip()
        except Exception as e:LOG(e)
        
        self.gpt_key = QLineEdit(oai_key)
        self.gpt_key.setPlaceholderText("Enter OpenAI key here…")
        self.gpt_key.editingFinished.connect(self.save_gpt_key)
        
        self.gpt_prompt = QTextEdit()
        self.gpt_prompt.setPlaceholderText("Enter GPT prompt text here…")
        
        gpt_gen = QPushButton(QIcon(PDIR+"assets/send-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Generate")
        gpt_gen.clicked.connect(self.generate_gpt)
        self.IconButtons.append({"icon_path":"assets/send-","button":gpt_gen})
        
        self.gpt_model = ComboBox(self)
        try:
            self.gpt_model.addItems(self.gpt_get_models(oai_key))
        except Exception as e:LOG(e)
        
        gpt_gen_layout = QHBoxLayout()
        gpt_gen_layout.addWidget(gpt_gen)
        gpt_gen_layout.addWidget(self.gpt_model)
        
        self.gpt_output = QTextEdit()
        self.gpt_output.setPlaceholderText("Outputted generation will appear here.")
        self.gpt_output.setReadOnly(True)
        
        gpt_set_output = QPushButton(QIcon(PDIR+"assets/set-msg-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Overwrite")
        gpt_copy_output = QPushButton(QIcon(PDIR+"assets/copy-"+("light" if COLORS["Button"].lightness() >= 128 else "dark")),"Copy")
        gpt_set_output.clicked.connect(self.set_from_output)
        gpt_copy_output.clicked.connect(self.copy_output)
        self.IconButtons.append({"icon_path":"assets/set-msg-","button":gpt_set_output})
        self.IconButtons.append({"icon_path":"assets/copy-","button":gpt_copy_output})
        
        gpt_btns_layout = QHBoxLayout()
        gpt_btns_layout.addWidget(gpt_set_output)
        gpt_btns_layout.addWidget(gpt_copy_output)
        
        gpt_layout = QVBoxLayout()
        gpt_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        gpt_layout.addWidget(self.gpt_key)
        gpt_layout.addWidget(self.gpt_prompt)
        gpt_layout.addLayout(gpt_gen_layout)
        gpt_layout.addWidget(self.gpt_output)
        gpt_layout.addLayout(gpt_btns_layout)
        
        self.gpt.setLayout(gpt_layout)
        
        open_gpt.clicked.connect(self.show_gpt)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.run_btn)
        btns_layout.addWidget(self.save_btn)
        btns_layout.addWidget(self.save_p_btn)
        btns_layout.addWidget(self.pref_btn)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.addWidgets(layout,[l,input_label,self.text_input,open_gpt,voice_label,self.voice])
        layout.addLayout(output_name_label_layout)
        self.addWidgets(layout,[self.output_input,output_label,self.output,model_label,self.model])
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
        except Exception as e:LOG(e)

        self.MODELS = []
        req = requests.get("https://api.elevenlabs.io/v1/models",headers={"xi-api-key": self.key, "Content-Type": "application/json"})
        for x in req.json():
            if x["can_do_text_to_speech"]:
                self.MODELS.append([x["model_id"],x["name"]])
                self.model.addItem(x["name"])
        self.model.setCurrentIndex(self.MODELS.index(self.data["voice_model"]))

    def gpt_get_models(self,oai_key:str):
        gpt_models = []
        with OpenAI(api_key=oai_key) as client:
            for x in client.models.list().data:
                if x.id.startswith("gpt-"):
                    gpt_models.append(x.id)
        return gpt_models
    
    def update_widget_style(self):
        self.prefer["WidgetStyle"] = self.pref_widget_style.currentText()
        if not self.prefer["WidgetStyle"] in ["Default","System"]:
            app.setStyle(self.prefer["WidgetStyle"])
        else:
            app.setStyle(DEFAULT_STYLE if self.prefer["WidgetStyle"] == "System" else "Fusion")
    
    # def toggle_native(self):
    #     self.prefer["NativeWidgets"] = self.pref_native.isChecked()
    #     if self.prefer["NativeWidgets"]:
    #         app.setStyle(DEFAULT_STYLE)
    #     else:
    #         app.setStyle("fusion")
        # if (app.style().name() == "fusion" and not self.prefer["NativeWidgets"]) or (app.style().name() != "fusion" and self.prefer["NativeWidgets"]): return
        # x = QMessageBox.question(self,"PyaiiTTS | Apply Preferences","PyaiiTTS requires a restart to apply certain preferences.\nClose PyaiiTTS now?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
        # if x == QMessageBox.StandardButton.Yes:
        #     if QMessageBox.question(self,"PyaiiTTS | Apply Preferences","Save configuration?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes: self.save()
        #     if QMessageBox.question(self,"PyaiiTTS | Apply Preferences","Save preferences?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes: self.save_p()
        #     sys.exit()
    
    def set_voice_settings(self,x:int):
        if x == 0:
            self.data["voice_stability"] = self.stability.value()
        elif x == 1:
            self.data["voice_similarity"] = self.similarity.value()
    
    def change_model(self):
        self.data["voice_model"] = self.MODELS[self.model.currentIndex()]
    
    def open_prg_dir(self):
        if sys.platform == "win32":
            os.startfile(PDIR)
        elif sys.platform == "darwin":
            os.system(f"open {PDIR}")
        else:
            os.system(f"xdg-open {PDIR}")
    
    def reset(self):
        x = QMessageBox.warning(self,"PyaiiTTS | Reset All","Are you sure you want to reset EVERYTHING?\nNote: your API key(s) will not be reset.",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
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
            if os.path.exists(PDIR+v):
                os.remove(PDIR+v)
        z = QMessageBox.question(self,"PyaiiTTS","Quit PyaiiTTs now?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
        if z != QMessageBox.StandardButton.Yes: return
        self.close()
        sys.exit()

    def save_gpt_key(self):
        with open(PDIR+"openai-key.txt","w") as f:
            f.write(self.gpt_key.text().strip())
        if self.gpt_model.count() < 1:
            self.gpt_model.clear()
            self.gpt_model.addItems(self.gpt_get_models(self.gpt_key.text().strip()))

    def deserialize_theme(self,name:str) -> dict:
        if not name in THEMES: return
        theme:dict = THEMES[name].copy()
        for i, v in theme.items():
            theme[i] = v.get()
        return theme
    
    def serialize_theme(self,data:dict[str,RGB]) -> dict:
        for i, v in data.items():
            data[i] = RGB(v)
        return data
    
    def dump_THEMES(self):
        _themes = THEMES.copy()
        for k,v in _themes.items():
            for y, x in v.items():
                _themes[k][y] = x.get()
        try:
            with open(PDIR+"themes.json","w") as f:
                json.dump(_themes,f,indent=4)
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
                self.apply_theme(list(THEMES.keys())[(ind-1 if list(THEMES.keys())[ind-1] != SYSTEM_THEME else 0) if ind > 0 else 0])
                self.pref_t.setCurrentIndex(
                    list(THEMES.keys()).index(self.prefer["Theme"])
                )
            self.pref_t.removeItem(ind)
            QMessageBox.information(self,"PyaiiTTS | Remove Theme",f"Theme '{name}' removed successfully!")
        else:
            QMessageBox.critical(self,"PyaiiTTS | Remove Theme",f"Invalid theme '{name}'!")

    def save_theme(self,_name:str=None,_data:dict[str,RGB]=None,_silence_popups:bool=False) -> bool:
        name = _name
        if not _name:
            name, s = QInputDialog.getText(self,"PyaiiTTS | Save Theme","Save Theme as:")
            if not s: return False
        if name in PROTECTED_THEMES:
            QMessageBox.critical(self,"PyaiiTTS | Save Theme",f"Failed to save theme: invalid name '{name}'.",QMessageBox.StandardButton.Close)
            return False
        overwrite = False
        if name in list(THEMES.keys()):
            x = QMessageBox.warning(self,"PyaiiTTS | Save Theme",f"Overwrite existing theme '{name}'?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
            if x != QMessageBox.StandardButton.Yes: return False
            overwrite = True
        THEMES[name] = COLORS if not _data else _data
        self.apply_theme(name)
        e = self.dump_THEMES()
        if e: QErrorMessage(self).showMessage(str(e)); return False
        if not overwrite: self.pref_t.addItem(name)
        self.pref_t.setCurrentIndex(
            list(THEMES.keys()).index(self.prefer["Theme"])
        )
        if not _silence_popups: QMessageBox.information(self,"PyaiiTTS | Save Theme",f"Theme '{name}' saved and applied successfully!")
        return True
    
    def export_theme(self):
        try:
            name, s = QInputDialog.getText(self,"PyaiiTTS | Export Theme","Theme to export:")
            if not s: return
            if not name in THEMES.keys():
                QMessageBox.critical(self,"PyaiiTTS | Export Theme",f"Failed to export theme: theme {name} does not exist!",QMessageBox.StandardButton.Close)
                return
            e_path = (USER+"Downloads" if os.path.exists(USER+"Downloads") else PDIR)+name+".pyaiitheme"
            fp,_ = QFileDialog.getSaveFileName(self,"Export theme as…",e_path,"PyaiiTTS Themes (*.pyaiitheme);;All Files (*)","*.pyaiitheme")
            if not fp: return
            f = open(fp,"w")
            json.dump(self.deserialize_theme(name),f,indent=4)
            QMessageBox.information(self,"PyaiiTTS | Export Theme",f"Theme '{name}' exported to {fp} successfully!")
        except Exception as e:
            QErrorMessage(self).showMessage(str(e))
    
    def import_theme(self):
        try:
            fp,_ = QFileDialog.getOpenFileName(self,"Choose a theme to import…",PDIR,"PyaiiTTS Themes (*.pyaiitheme)","*.pyaiitheme")
            if not os.path.exists(fp): return
            f = open(fp, "r")
            name = f.name[f.name.rfind("/")+1:f.name.rfind('.pyaiitheme')]
            data = self.serialize_theme(json.load(f))
            r = self.save_theme(name,data,True)
            if not r: return
            QMessageBox.information(self,"PyaiiTTS | Import Theme",f"Theme '{name}' imported successfully!")
        except Exception as e:
            QErrorMessage(self).showMessage(str(e))
        

    def apply_current_theme(self,x:QComboBox):
        self.apply_theme(x.currentText())

    def apply_theme(self,t:str):
        global COLORS, THEME_CHANGED
        last_theme = self.prefer["Theme"]
        self.prefer["Theme"] = t
        # if t == SYSTEM_THEME and THEME_CHANGED:
        #     x = QMessageBox.question(self,"PyaiiTTS","Quit PyaiiTTs now?\nYour configurations and preferences will be saved.",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
        #     if x == QMessageBox.StandardButton.Yes:
        #         self.save()
        #         self.save_p()
        #         self.close()
        #         sys.exit()
        #     else:
        #         self.apply_theme(last_theme)
        #         try:
        #             self.pref_t.setCurrentIndex(
        #                 list(THEMES.keys()).index(self.prefer["Theme"])
        #             )
        #          Exception as e:LOG(e)
        # else:
        #^
        COLORS = THEMES[t].copy()
        self.set_style()
        THEME_CHANGED = True

    def addWidgets(self,x:QHBoxLayout|QVBoxLayout,y:list[QWidget|QVBoxLayout|QHBoxLayout]):
        for v in y:
            if type(v) != QVBoxLayout and type(v) != QHBoxLayout:
                x.addWidget(v)
            else:
                x.addLayout(v)

    def show_pref(self):
        self.pref.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),(self.y()+int((self.height()-(self.height()/1.1))/2)),0,0)
        self.pref.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))
        self.toggle_el(self.pref)
        
    def show_gpt(self):
        self.gpt.setGeometry(self.x()+int((self.width()-(self.width()/1.1))/2),(self.y()+int((self.height()-(self.height()/1.1))/2)),0,0)
        self.gpt.setFixedSize(int(self.width()/1.1),int(self.height()/1.1))
        self.toggle_el(self.gpt)

    def get_style(self):
        x=""
        for n,v in COLOR_FUNCTIONS.items():
            if n != "Background":
                x+=v(n)
        return COLOR_FUNCTIONS["Background"]("Background")+x

    def set_style(self):
        if self.prefer["Theme"] != SYSTEM_THEME:
            self.setStyleSheet(self.get_style())
        else:
            self.setStyleSheet("")
        for c,v in self.pref_c.items():
            if self.prefer["Theme"] != SYSTEM_THEME:
                z="white"
                if COLORS[c].lightness() >= 128:
                    z="black"
                v.setStyleSheet(f'background-color: {COLORS[c].QColor().name()}; color: {z};')
            else:
                v.setStyleSheet("")
        for x in self.ComboBoxes:
            if self.prefer["Theme"] != SYSTEM_THEME:
                x.view().parentWidget().setStyleSheet(f'background-color: {COLORS["Background"].QColor().name()}')
            else:
                x.view().parentWidget().setStyleSheet("")
        for x in self.IconButtons:
            if self.prefer["Theme"] != SYSTEM_THEME:
                x["button"].setIcon(QIcon(PDIR+x["icon_path"]+("light" if COLORS["Button"].lightness() >= 128 else "dark")))
            

    def change_c(self,c:str):
        def x(y:QColor):
            COLORS[c] = RGB(y)
            self.set_style()
            # self.setStyleSheet(self.get_style())
            # z="white"
            # if COLORS[c].lightness() >= 128:
            #     z="black"
            # self.pref_c[c].setStyleSheet(f'background-color: {COLORS[c].QColor().name()}; color: {z};')
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
        file_path = f"{self.data["output_path"]}/{self.data["output_name"]}.mp3"
        if os.path.exists(self.data["output_path"]+"/"+self.data["output_name"]+".mp3"):
            self.output_name_icon.setToolTip(f"WARNING: File {file_path} already exists!\nGenerating will overwrite this file.")
            self.output_name_icon.setVisible(True)
        else:
            self.output_name_icon.setVisible(False)

    def upd_text(self):
        escapes = ''.join([chr(char) for char in range(1, 32)])
        self.data["text"] = self.text_input.toPlainText().encode('unicode_escape').decode('utf-8')
        self.data["text"] = self.data["text"].translate(str.maketrans('','',escapes))
        self.text_input.setPlainText(self.data["text"].encode('utf-8').decode('unicode_escape'))

    def choose_dir(self):
        dia = QFileDialog.getExistingDirectory(self,"Choose output directory…",self.data["output_path"])
        if dia:
            self.data["output_path"] = dia
            self.output.setText(f'Choose Output Location ({self.data["output_path"]})')

    def generate(self):
        self.save()
        voice_settings = VoiceSettings(stability=self.data['voice_stability'],similarity_boost=self.data['voice_similarity'])
        x=self.client.generate(text=self.data["text"],voice=self.data["voice_id"],voice_settings=voice_settings,model=self.data['voice_model'][0])
        with open(f"{self.data['output_path']}/{self.data['output_name']}.mp3","wb") as f:
            f.write(b''.join(x))
            QMessageBox.information(self,"PyaiiTTS","TTS Success!")
    
    def generate_gpt(self):
        key,prompt = self.gpt_key.text().strip(),self.gpt_prompt.toPlainText().strip()
        LOG("Start GPT Gen…")
        with OpenAI(api_key=key) as client:
            chat_completion = client.chat.completions.create(
                messages=[{
                    "role":"user",
                    "content":prompt
                }],
                model=self.gpt_model.currentText().strip()
            )
        self.gpt_output.setText(chat_completion.choices[0].message.content)
        LOG("Finish GPT Gen.")

    def copy_output(self):
        pyclip.copy(self.gpt_output.toPlainText().strip())

    def set_from_output(self):
        self.text_input.setPlainText(self.gpt_output.toPlainText().strip())

    def save_p(self):
        try:
            # self.setWindowTitle("PyaiiTTS")
            # prefer = {"Theme": self.prefer["Theme"]}
            with open(PDIR+"pref.json","w") as f:
                json.dump(self.prefer,f,indent=4)
            QMessageBox.information(self,"PyaiiTTS","Successfully Saved Preferences",QMessageBox.StandardButton.Ok)
        except Exception as e:
            QErrorMessage(self).showMessage(str(e))
            # QMessageBox.critical(self,"PyaiiTTS",str(e),QMessageBox.StandardButton.Close)

    def save(self):
        try:
            self.upd_text()
            self.upd_file()
            self.change_voice()
            # self.setWindowTitle("PyaiiTTS")
            # data = {"output_path": self.data["output_path"], "voice_id": self.data["voice_id"], "text": self.data["text"], "output_name": self.data["output_name"]}
            with open(PDIR+"conf.json","w") as f:
                json.dump(self.data,f,indent=4)
            QMessageBox.information(self,"PyaiiTTS","Successfully Saved Configurations",QMessageBox.StandardButton.Ok)
        except Exception as e:
            QErrorMessage(self).showMessage(str(e))
            # QMessageBox.critical(self,str(e),QMessageBox.StandardButton.Close)

class ComboBox(QComboBox):
    def __init__(self,app:MainWindow):
        super().__init__()
        app.ComboBoxes.append(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
