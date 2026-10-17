import os
import sys
import cv2
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QCheckBox, QFileDialog, QProgressBar,
    QComboBox, QFrame, QColorDialog)
from detector import detect_people, draw_detections
from settings import load_settings, save_settings

STYLE = """
QWidget { background:#0b0d12; color:#e4e8f1; font-family:'Segoe UI'; font-size:13px; }
QFrame#panel { background:#11151d; border:1px solid #252d3a; border-radius:12px; }
QLabel#title { font-size:25px; font-weight:700; color:#f4f7ff; }
QLabel#muted { color:#7f8b9f; }
QPushButton { background:#171e29; border:1px solid #2b3848; border-radius:8px; padding:10px 14px; color:#d9e2ef; }
QPushButton:hover { border-color:#00dcb7; color:#00ffd2; }
QPushButton#primary { background:#00c7a4; color:#07110f; font-weight:700; border:0; }
QPushButton#primary:hover { background:#00e6bf; }
QCheckBox { spacing:9px; }
QCheckBox::indicator { width:38px; height:20px; border-radius:10px; background:#303744; }
QCheckBox::indicator:checked { background:#00c7a4; }
QSlider::groove:horizontal { height:4px; background:#29313e; border-radius:2px; }
QSlider::handle:horizontal { background:#00ffd2; width:14px; margin:-5px 0; border-radius:7px; }
QProgressBar { border:0; background:#202733; height:6px; border-radius:3px; text-align:center; }
QProgressBar::chunk { background:#00dcb7; border-radius:3px; }
QComboBox { padding:8px; background:#171e29; border:1px solid #2b3848; border-radius:7px; }
"""


class Processor(QThread):
    frame = Signal(object, int, int)
    done = Signal(str)
    def __init__(self, path, detection, confidence, color, opacity, sample_step):
        super().__init__(); self.path=path; self.detection=detection; self.confidence=confidence; self.color=color; self.opacity=opacity; self.sample_step=sample_step; self.stopped=False
    def stop(self): self.stopped=True
    def run(self):
        ext=os.path.splitext(self.path)[1].lower()
        if ext in ('.png','.jpg','.jpeg','.bmp','.webp'):
            image=cv2.imread(self.path)
            if image is None: self.done.emit('Could not open image'); return
            boxes=detect_people(image,self.confidence) if self.detection else []
            self.frame.emit(draw_detections(image,boxes,self.color,self.opacity) if boxes else image,1,1)
            self.done.emit(f'Complete · {len(boxes)} person(s) detected'); return
        cap=cv2.VideoCapture(self.path)
        total=max(1,int(cap.get(cv2.CAP_PROP_FRAME_COUNT))); count=0; sampled=0
        while not self.stopped:
            ok, image=cap.read()
            if not ok: break
            count+=1
            if count % self.sample_step: continue
            boxes=detect_people(image,self.confidence) if self.detection else []
            self.frame.emit(draw_detections(image,boxes,self.color,self.opacity) if boxes else image,count,total); sampled+=1
        cap.release(); self.done.emit('Stopped' if self.stopped else f'Complete · sampled {sampled} frames')


class App(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('NeonFrame'); self.resize(1180,760); self.setMinimumSize(900,600)
        self.s=load_settings(); self.path=''; self.thread=None; self.last_image=None
        root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root); outer.setContentsMargins(28,24,28,24); outer.setSpacing(18)
        header=QHBoxLayout(); brand=QVBoxLayout(); title=QLabel('NEONFRAME'); title.setObjectName('title'); subtitle=QLabel('LOCAL MEDIA ANALYSIS  /  SAFE REVIEW MODE'); subtitle.setObjectName('muted'); brand.addWidget(title); brand.addWidget(subtitle); header.addLayout(brand); header.addStretch()
        self.master=QCheckBox('OVERLAY'); self.master.setChecked(self.s['overlay_enabled']); header.addWidget(self.master); outer.addLayout(header)
        body=QHBoxLayout(); body.setSpacing(18); outer.addLayout(body,1)
        preview=QFrame(); preview.setObjectName('panel'); pv=QVBoxLayout(preview); pv.setContentsMargins(16,16,16,16)
        bar=QHBoxLayout(); self.file_label=QLabel('NO MEDIA LOADED'); self.file_label.setObjectName('muted'); self.status=QLabel('● READY'); self.status.setStyleSheet('color:#00dcb7;font-weight:700'); bar.addWidget(self.file_label); bar.addStretch(); bar.addWidget(self.status); pv.addLayout(bar)
        self.image=QLabel('OPEN A SCREENSHOT OR RECORDING\n\nLocal processing · no game capture'); self.image.setAlignment(Qt.AlignCenter); self.image.setStyleSheet('color:#536073;background:#090b10;border-radius:8px;'); self.image.setMinimumSize(500,400); pv.addWidget(self.image,1)
        self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); pv.addWidget(self.progress)
        controls=QHBoxLayout(); self.open_btn=QPushButton('＋  Open media'); self.open_btn.clicked.connect(self.open_media); controls.addWidget(self.open_btn); self.start_btn=QPushButton('▶  Start analysis'); self.start_btn.setObjectName('primary'); self.start_btn.clicked.connect(self.start); controls.addWidget(self.start_btn); self.stop_btn=QPushButton('■  Stop'); self.stop_btn.clicked.connect(self.stop); controls.addWidget(self.stop_btn); self.export_btn=QPushButton('↓  Export frame'); self.export_btn.clicked.connect(self.export); controls.addWidget(self.export_btn); pv.addLayout(controls); body.addWidget(preview,1)
        panel=QFrame(); panel.setObjectName('panel'); panel.setFixedWidth(270); side=QVBoxLayout(panel); side.setContentsMargins(18,18,18,18); side.setSpacing(13)
        h=QLabel('CONFIGURATION'); h.setStyleSheet('font-weight:700;color:#00ffd2;letter-spacing:1px'); side.addWidget(h)
        self.detect=QCheckBox('Character detection'); self.detect.setChecked(self.s['detection_enabled']); side.addWidget(self.detect)
        side.addWidget(self.label('Detection confidence')); self.conf=QSlider(Qt.Horizontal); self.conf.setRange(10,90); self.conf.setValue(self.s['confidence']); side.addWidget(self.conf); self.confval=QLabel(); side.addWidget(self.confval); self.conf.valueChanged.connect(lambda x:self.confval.setText(f'{x}%'))
        side.addWidget(self.label('Overlay opacity')); self.opacity=QSlider(Qt.Horizontal); self.opacity.setRange(20,100); self.opacity.setValue(self.s['opacity']); side.addWidget(self.opacity); self.opval=QLabel(); side.addWidget(self.opval); self.opacity.valueChanged.connect(lambda x:self.opval.setText(f'{x}%'))
        side.addWidget(self.label('Bounding box color')); colorrow=QHBoxLayout(); self.color_btn=QPushButton('  ●  Choose color'); self.color_btn.clicked.connect(self.choose_color); colorrow.addWidget(self.color_btn); side.addLayout(colorrow)
        side.addWidget(self.label('Video sampling')); self.sampling=QComboBox(); self.sampling.addItems(['Every 6 frames','Every 3 frames','Every frame']); self.sampling.setCurrentIndex(max(0,min(2,int(self.s.get('sampling',0))))); side.addWidget(self.sampling)
        side.addStretch(); note=QLabel('Works only with files you select. No game hooks, memory access, or anti-cheat interaction.'); note.setWordWrap(True); note.setObjectName('muted'); side.addWidget(note); body.addWidget(panel)
        self.confval.setText(f"{self.conf.value()}%"); self.opval.setText(f"{self.opacity.value()}%"); self.set_color(self.s['box_color'])
        for w in (self.master,self.detect,self.conf,self.opacity):
            if isinstance(w,QCheckBox): w.stateChanged.connect(self.persist)
            else: w.valueChanged.connect(self.persist)
    def label(self,t):
        x=QLabel(t); x.setObjectName('muted'); return x
    def set_color(self,c):
        q=QColor(c); self.box_color=(q.blue(),q.green(),q.red()); self.color_btn.setStyleSheet(f'color:{c};border-color:{c}')
    def choose_color(self):
        c=QColorDialog.getColor(QColor(self.s['box_color']),self,'Bounding box color')
        if c.isValid(): self.s['box_color']=c.name(); self.set_color(c.name()); self.persist()
    def persist(self,*_):
        self.s.update(overlay_enabled=self.master.isChecked(),detection_enabled=self.detect.isChecked(),opacity=self.opacity.value(),confidence=self.conf.value(),sampling=self.sampling.currentIndex())
        save_settings(self.s)
    def open_media(self):
        p,_=QFileDialog.getOpenFileName(self,'Open media','','Media (*.png *.jpg *.jpeg *.bmp *.webp *.mp4 *.avi *.mov *.mkv)')
        if p: self.path=p; self.file_label.setText(os.path.basename(p)); self.status.setText('● FILE READY')
    def start(self):
        if not self.path: self.open_media()
        if not self.path:return
        self.stop(); self.status.setText('● PROCESSING'); steps=(6,3,1); self.thread=Processor(self.path,self.detect.isChecked() and self.master.isChecked(),self.conf.value()/100,self.box_color,self.opacity.value()/100,steps[self.sampling.currentIndex()]); self.thread.frame.connect(self.show_frame); self.thread.done.connect(self.finished); self.thread.start()
    def stop(self):
        if self.thread and self.thread.isRunning(): self.thread.stop(); self.thread.wait(1500)
    def show_frame(self,frame,current,total):
        self.last_image=frame; h,w=frame.shape[:2]; rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); q=QImage(rgb.data,w,h,3*w,QImage.Format_RGB888).copy(); self.image.setPixmap(QPixmap.fromImage(q).scaled(self.image.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.progress.setValue(int(current*100/total))
    def finished(self,text): self.status.setText('● '+text.upper()); self.progress.setValue(100)
    def export(self):
        if self.last_image is None:return
        p,_=QFileDialog.getSaveFileName(self,'Export annotated frame','NeonFrame-export.png','PNG (*.png)')
        if p: cv2.imwrite(p,self.last_image)
    def closeEvent(self,e): self.stop(); self.persist(); e.accept()

if __name__=='__main__':
    app=QApplication(sys.argv); app.setStyleSheet(STYLE); window=App(); window.show(); sys.exit(app.exec())
