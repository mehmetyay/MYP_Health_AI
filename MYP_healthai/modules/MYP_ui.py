#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Ana Kullanıcı Arayüzü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QProgressBar, QTabWidget, QFileDialog, QMessageBox,
    QGroupBox, QScrollArea, QSplitter, QFrame, QLineEdit, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup, QSlider, QDateEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from utils.MYP_language_manager import LanguageManager
from modules.MYP_data_loader import DataLoader
from modules.MYP_analysis_engine import AnalysisEngine
from modules.MYP_report_generator import ReportGenerator

class AnalysisWorker(QThread):
    """Analiz işlemlerini arka planda çalıştıran thread"""
    progress_updated = pyqtSignal(int)
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data, symptoms, lifestyle_data):
        super().__init__()
        self.data = data
        self.symptoms = symptoms
        self.lifestyle_data = lifestyle_data
        self.analysis_engine = AnalysisEngine()
    
    def run(self):
        try:
            self.progress_updated.emit(10)
            
            # Veri ön işleme
            processed_data = self.analysis_engine.preprocess_data(self.data)
            self.progress_updated.emit(30)
            
            # Semptom analizi
            symptom_analysis = self.analysis_engine.analyze_symptoms(self.symptoms)
            self.progress_updated.emit(50)
            
            # Risk analizi
            risk_analysis = self.analysis_engine.calculate_risk_score(
                processed_data, self.lifestyle_data
            )
            self.progress_updated.emit(70)
            
            # Teşhis tahmini
            diagnosis_prediction = self.analysis_engine.predict_diagnosis(
                processed_data, symptom_analysis
            )
            self.progress_updated.emit(90)
            
            # Öneriler oluştur
            recommendations = self.analysis_engine.generate_recommendations(
                risk_analysis, diagnosis_prediction, self.lifestyle_data
            )
            self.progress_updated.emit(100)
            
            # Sonuçları birleştir
            results = {
                'risk_analysis': risk_analysis,
                'symptom_analysis': symptom_analysis,
                'diagnosis_prediction': diagnosis_prediction,
                'recommendations': recommendations,
                'processed_data': processed_data
            }
            
            self.analysis_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class HealthAIApplication(QMainWindow):
    """Ana sağlık AI uygulaması"""
    
    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.data_loader = DataLoader()
        self.report_generator = ReportGenerator()
        
        self.current_data = None
        self.analysis_results = None
        
        self.init_ui()
        self.setup_styles()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("MYP Sağlık Yapay Zeka Sistemi v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Üst panel - Dil seçimi ve başlık
        self.create_header_panel(main_layout)
        
        # Ana içerik alanı
        self.create_main_content(main_layout)
        
        # Alt durum çubuğu
        self.create_status_bar()
        
    def create_header_panel(self, parent_layout):
        """Üst panel oluştur"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Logo ve başlık
        title_label = QLabel("🏥 MYP Sağlık Yapay Zeka Sistemi")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        # Dil seçimi
        lang_label = QLabel("Dil / Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English", "Deutsch", "Kurdî", "Русский"])
        self.language_combo.currentTextChanged.connect(self.change_language)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(lang_label)
        header_layout.addWidget(self.language_combo)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_content(self, parent_layout):
        """Ana içerik alanını oluştur"""
        # Tab widget oluştur
        self.tab_widget = QTabWidget()
        
        # Veri Yükleme Sekmesi
        self.create_data_tab()
        
        # Semptom Girişi Sekmesi
        self.create_symptoms_tab()
        
        # Yaşam Tarzı Sekmesi
        self.create_lifestyle_tab()
        
        # Analiz Sekmesi
        self.create_analysis_tab()
        
        # Sonuçlar Sekmesi
        self.create_results_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_data_tab(self):
        """Veri yükleme sekmesi"""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)
        
        # Veri yükleme grubu
        data_group = QGroupBox("📁 Veri Yükleme")
        data_group_layout = QVBoxLayout(data_group)
        
        # Dosya seçim butonları
        file_buttons_layout = QHBoxLayout()
        
        self.load_genetic_btn = QPushButton("🧬 Genetik Veri Yükle")
        self.load_genetic_btn.clicked.connect(lambda: self.load_data_file('genetic'))
        
        self.load_medical_btn = QPushButton("🏥 Tıbbi Geçmiş Yükle")
        self.load_medical_btn.clicked.connect(lambda: self.load_data_file('medical'))
        
        self.load_family_btn = QPushButton("👨‍👩‍👧‍👦 Aile Geçmişi Yükle")
        self.load_family_btn.clicked.connect(lambda: self.load_data_file('family'))
        
        file_buttons_layout.addWidget(self.load_genetic_btn)
        file_buttons_layout.addWidget(self.load_medical_btn)
        file_buttons_layout.addWidget(self.load_family_btn)
        
        data_group_layout.addLayout(file_buttons_layout)
        
        # Veri önizleme tablosu
        self.data_preview_table = QTableWidget()
        self.data_preview_table.setMaximumHeight(200)
        data_group_layout.addWidget(QLabel("📊 Yüklenen Veri Önizlemesi:"))
        data_group_layout.addWidget(self.data_preview_table)
        
        layout.addWidget(data_group)
        layout.addStretch()
        
        self.tab_widget.addTab(data_widget, "📁 Veri Yükleme")
    
    def create_symptoms_tab(self):
        """Semptom girişi sekmesi"""
        symptoms_widget = QWidget()
        layout = QVBoxLayout(symptoms_widget)
        
        # Semptom girişi grubu
        symptoms_group = QGroupBox("🩺 Semptom ve Şikayet Girişi")
        symptoms_layout = QVBoxLayout(symptoms_group)
        
        # Serbest metin girişi
        symptoms_layout.addWidget(QLabel("Yaşadığınız belirtileri detaylı olarak açıklayın:"))
        self.symptoms_text = QTextEdit()
        self.symptoms_text.setPlaceholderText(
            "Örnek: Başım ağrıyor, yorgunluk hissediyorum, uykusuzluk yaşıyorum, "
            "iştahsızlık var, bazen nefes darlığı oluyor..."
        )
        self.symptoms_text.setMaximumHeight(150)
        symptoms_layout.addWidget(self.symptoms_text)
        
        # Hızlı semptom seçimi
        quick_symptoms_layout = QGridLayout()
        symptoms_layout.addWidget(QLabel("🔍 Hızlı Semptom Seçimi:"))
        
        common_symptoms = [
            "Baş ağrısı", "Yorgunluk", "Ateş", "Öksürük", "Nefes darlığı",
            "Karın ağrısı", "Bulantı", "Baş dönmesi", "Kas ağrısı", "Uykusuzluk",
            "İştahsızlık", "Stres", "Anksiyete", "Depresyon", "Konsantrasyon sorunu"
        ]
        
        self.symptom_checkboxes = {}
        for i, symptom in enumerate(common_symptoms):
            checkbox = QCheckBox(symptom)
            checkbox.stateChanged.connect(self.update_symptoms_text)
            self.symptom_checkboxes[symptom] = checkbox
            quick_symptoms_layout.addWidget(checkbox, i // 3, i % 3)
        
        symptoms_layout.addLayout(quick_symptoms_layout)
        
        # Semptom şiddeti
        severity_layout = QHBoxLayout()
        severity_layout.addWidget(QLabel("Genel Şiddet (1-10):"))
        self.severity_slider = QSlider(Qt.Horizontal)
        self.severity_slider.setRange(1, 10)
        self.severity_slider.setValue(5)
        self.severity_label = QLabel("5")
        self.severity_slider.valueChanged.connect(
            lambda v: self.severity_label.setText(str(v))
        )
        severity_layout.addWidget(self.severity_slider)
        severity_layout.addWidget(self.severity_label)
        symptoms_layout.addLayout(severity_layout)
        
        layout.addWidget(symptoms_group)
        layout.addStretch()
        
        self.tab_widget.addTab(symptoms_widget, "🩺 Semptomlar")
    
    def create_lifestyle_tab(self):
        """Yaşam tarzı sekmesi"""
        lifestyle_widget = QWidget()
        layout = QVBoxLayout(lifestyle_widget)
        
        # Scroll area oluştur
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Temel bilgiler
        basic_group = QGroupBox("👤 Temel Bilgiler")
        basic_layout = QGridLayout(basic_group)
        
        basic_layout.addWidget(QLabel("Yaş:"), 0, 0)
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(30)
        basic_layout.addWidget(self.age_spin, 0, 1)
        
        basic_layout.addWidget(QLabel("Cinsiyet:"), 0, 2)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Erkek", "Kadın", "Diğer"])
        basic_layout.addWidget(self.gender_combo, 0, 3)
        
        basic_layout.addWidget(QLabel("Boy (cm):"), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 250)
        self.height_spin.setValue(170)
        basic_layout.addWidget(self.height_spin, 1, 1)
        
        basic_layout.addWidget(QLabel("Kilo (kg):"), 1, 2)
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(30, 300)
        self.weight_spin.setValue(70)
        basic_layout.addWidget(self.weight_spin, 1, 3)
        
        scroll_layout.addWidget(basic_group)
        
        # Yaşam tarzı alışkanlıkları
        habits_group = QGroupBox("🚭 Alışkanlıklar")
        habits_layout = QGridLayout(habits_group)
        
        # Sigara
        habits_layout.addWidget(QLabel("Sigara:"), 0, 0)
        self.smoking_combo = QComboBox()
        self.smoking_combo.addItems(["Hiç içmem", "Bıraktım", "Ara sıra", "Günlük"])
        habits_layout.addWidget(self.smoking_combo, 0, 1)
        
        # Alkol
        habits_layout.addWidget(QLabel("Alkol:"), 0, 2)
        self.alcohol_combo = QComboBox()
        self.alcohol_combo.addItems(["Hiç içmem", "Nadiren", "Haftalık", "Günlük"])
        habits_layout.addWidget(self.alcohol_combo, 0, 3)
        
        # Egzersiz
        habits_layout.addWidget(QLabel("Egzersiz (haftalık):"), 1, 0)
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(["Hiç", "1-2 gün", "3-4 gün", "5+ gün"])
        habits_layout.addWidget(self.exercise_combo, 1, 1)
        
        # Uyku
        habits_layout.addWidget(QLabel("Günlük uyku (saat):"), 1, 2)
        self.sleep_spin = QSpinBox()
        self.sleep_spin.setRange(3, 12)
        self.sleep_spin.setValue(8)
        habits_layout.addWidget(self.sleep_spin, 1, 3)
        
        scroll_layout.addWidget(habits_group)
        
        # Beslenme
        nutrition_group = QGroupBox("🍎 Beslenme")
        nutrition_layout = QVBoxLayout(nutrition_group)
        
        nutrition_questions = [
            "Düzenli öğün yersiniz",
            "Bol sebze-meyve tüketirsiniz",
            "Fast food sık tüketirsiniz",
            "Bol su içersiniz",
            "Vitamin takviyesi alırsınız"
        ]
        
        self.nutrition_checkboxes = {}
        for question in nutrition_questions:
            checkbox = QCheckBox(question)
            self.nutrition_checkboxes[question] = checkbox
            nutrition_layout.addWidget(checkbox)
        
        scroll_layout.addWidget(nutrition_group)
        
        # Stres ve ruh hali
        mental_group = QGroupBox("🧠 Ruh Hali ve Stres")
        mental_layout = QVBoxLayout(mental_group)
        
        mental_layout.addWidget(QLabel("Genel stres seviyeniz (1-10):"))
        self.stress_slider = QSlider(Qt.Horizontal)
        self.stress_slider.setRange(1, 10)
        self.stress_slider.setValue(5)
        self.stress_label = QLabel("5")
        self.stress_slider.valueChanged.connect(
            lambda v: self.stress_label.setText(str(v))
        )
        stress_layout = QHBoxLayout()
        stress_layout.addWidget(self.stress_slider)
        stress_layout.addWidget(self.stress_label)
        mental_layout.addLayout(stress_layout)
        
        mental_conditions = [
            "Depresyon geçmişi var",
            "Anksiyete sorunu yaşıyorum",
            "Uyku bozukluğu var",
            "Konsantrasyon sorunu yaşıyorum"
        ]
        
        self.mental_checkboxes = {}
        for condition in mental_conditions:
            checkbox = QCheckBox(condition)
            self.mental_checkboxes[condition] = checkbox
            mental_layout.addWidget(checkbox)
        
        scroll_layout.addWidget(mental_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(lifestyle_widget, "🏃‍♂️ Yaşam Tarzı")
    
    def create_analysis_tab(self):
        """Analiz sekmesi"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Analiz kontrolü
        control_group = QGroupBox("🔬 Analiz Kontrolü")
        control_layout = QVBoxLayout(control_group)
        
        # Analiz türü seçimi
        analysis_type_layout = QHBoxLayout()
        analysis_type_layout.addWidget(QLabel("Analiz Türü:"))
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Kapsamlı Analiz",
            "Hızlı Değerlendirme", 
            "Risk Analizi",
            "Semptom Odaklı"
        ])
        analysis_type_layout.addWidget(self.analysis_type_combo)
        control_layout.addLayout(analysis_type_layout)
        
        # Analiz başlat butonu
        self.start_analysis_btn = QPushButton("🚀 ANALİZİ BAŞLAT")
        self.start_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_analysis_btn.clicked.connect(self.start_analysis)
        control_layout.addWidget(self.start_analysis_btn)
        
        layout.addWidget(control_group)
        
        # İlerleme çubuğu
        progress_group = QGroupBox("📊 Analiz İlerlemesi")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Analiz bekleniyor...")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        # Analiz detayları
        details_group = QGroupBox("🔍 Analiz Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.analysis_details = QTextEdit()
        self.analysis_details.setReadOnly(True)
        self.analysis_details.setMaximumHeight(200)
        details_layout.addWidget(self.analysis_details)
        
        layout.addWidget(details_group)
        layout.addStretch()
        
        self.tab_widget.addTab(analysis_widget, "🔬 Analiz")
    
    def create_results_tab(self):
        """Sonuçlar sekmesi"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # Sonuç özeti
        summary_group = QGroupBox("📋 Analiz Özeti")
        summary_layout = QVBoxLayout(summary_group)
        
        self.results_summary = QTextEdit()
        self.results_summary.setReadOnly(True)
        self.results_summary.setMaximumHeight(150)
        summary_layout.addWidget(self.results_summary)
        
        layout.addWidget(summary_group)
        
        # Sonuç detayları için tab widget
        self.results_tab_widget = QTabWidget()
        
        # Risk analizi sekmesi
        self.risk_results_text = QTextEdit()
        self.risk_results_text.setReadOnly(True)
        self.results_tab_widget.addTab(self.risk_results_text, "⚠️ Risk Analizi")
        
        # Teşhis tahmini sekmesi
        self.diagnosis_results_text = QTextEdit()
        self.diagnosis_results_text.setReadOnly(True)
        self.results_tab_widget.addTab(self.diagnosis_results_text, "🩺 Teşhis Tahmini")
        
        # Öneriler sekmesi
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.results_tab_widget.addTab(self.recommendations_text, "💡 Öneriler")
        
        layout.addWidget(self.results_tab_widget)
        
        # Rapor oluşturma butonları
        report_buttons_layout = QHBoxLayout()
        
        self.generate_pdf_btn = QPushButton("📄 PDF Rapor Oluştur")
        self.generate_pdf_btn.clicked.connect(self.generate_pdf_report)
        self.generate_pdf_btn.setEnabled(False)
        
        self.generate_excel_btn = QPushButton("📊 Excel Rapor Oluştur")
        self.generate_excel_btn.clicked.connect(self.generate_excel_report)
        self.generate_excel_btn.setEnabled(False)
        
        report_buttons_layout.addWidget(self.generate_pdf_btn)
        report_buttons_layout.addWidget(self.generate_excel_btn)
        report_buttons_layout.addStretch()
        
        layout.addLayout(report_buttons_layout)
        
        self.tab_widget.addTab(results_widget, "📊 Sonuçlar")
    
    def create_status_bar(self):
        """Durum çubuğu oluştur"""
        self.statusBar().showMessage("MYP Sağlık AI Sistemi Hazır | Mehmet Yay © 2025")
    
    def setup_styles(self):
        """Uygulama stillerini ayarla"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
    
    def change_language(self, language):
        """Dil değiştir"""
        lang_codes = {
            "Türkçe": "tr",
            "English": "en", 
            "Deutsch": "de",
            "Kurdî": "ku",
            "Русский": "ru"
        }
        
        if language in lang_codes:
            self.lang_manager.set_language(lang_codes[language])
            self.update_ui_texts()
    
    def update_ui_texts(self):
        """UI metinlerini güncelle"""
        # Bu fonksiyon dil değişikliği sonrası tüm metinleri güncelleyecek
        pass
    
    def load_data_file(self, data_type):
        """Veri dosyası yükle"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            f"{data_type.title()} Veri Dosyası Seç",
            "",
            "Tüm Desteklenen (*.csv *.xlsx *.json *.xml);;CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;XML (*.xml)"
        )
        
        if file_path:
            try:
                data = self.data_loader.load_file(file_path, data_type)
                self.update_data_preview(data, data_type)
                self.statusBar().showMessage(f"{data_type.title()} verisi başarıyla yüklendi")
                
                # Mevcut verileri güncelle
                if not hasattr(self, 'loaded_data'):
                    self.loaded_data = {}
                self.loaded_data[data_type] = data
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yüklenirken hata oluştu:\n{str(e)}")
    
    def update_data_preview(self, data, data_type):
        """Veri önizlemesini güncelle"""
        if hasattr(data, 'head'):  # pandas DataFrame
            preview_data = data.head(10)
            self.data_preview_table.setRowCount(len(preview_data))
            self.data_preview_table.setColumnCount(len(preview_data.columns))
            self.data_preview_table.setHorizontalHeaderLabels(preview_data.columns.tolist())
            
            for i, row in enumerate(preview_data.itertuples(index=False)):
                for j, value in enumerate(row):
                    self.data_preview_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def update_symptoms_text(self):
        """Semptom metnini güncelle"""
        selected_symptoms = []
        for symptom, checkbox in self.symptom_checkboxes.items():
            if checkbox.isChecked():
                selected_symptoms.append(symptom)
        
        current_text = self.symptoms_text.toPlainText()
        if selected_symptoms:
            if current_text:
                new_text = current_text + ", " + ", ".join(selected_symptoms)
            else:
                new_text = ", ".join(selected_symptoms)
            self.symptoms_text.setPlainText(new_text)
    
    def collect_lifestyle_data(self):
        """Yaşam tarzı verilerini topla"""
        lifestyle_data = {
            'age': self.age_spin.value(),
            'gender': self.gender_combo.currentText(),
            'height': self.height_spin.value(),
            'weight': self.weight_spin.value(),
            'smoking': self.smoking_combo.currentText(),
            'alcohol': self.alcohol_combo.currentText(),
            'exercise': self.exercise_combo.currentText(),
            'sleep_hours': self.sleep_spin.value(),
            'stress_level': self.stress_slider.value(),
            'nutrition_habits': {k: v.isChecked() for k, v in self.nutrition_checkboxes.items()},
            'mental_conditions': {k: v.isChecked() for k, v in self.mental_checkboxes.items()}
        }
        return lifestyle_data
    
    def start_analysis(self):
        """Analizi başlat"""
        # Veri kontrolü
        if not hasattr(self, 'loaded_data') or not self.loaded_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce veri dosyalarını yükleyin!")
            return
        
        symptoms = self.symptoms_text.toPlainText().strip()
        if not symptoms:
            QMessageBox.warning(self, "Uyarı", "Lütfen semptomlarınızı girin!")
            return
        
        # UI'yi analiz moduna geçir
        self.start_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Analiz başlatılıyor...")
        
        # Yaşam tarzı verilerini topla
        lifestyle_data = self.collect_lifestyle_data()
        
        # Analiz worker'ını başlat
        self.analysis_worker = AnalysisWorker(
            self.loaded_data, symptoms, lifestyle_data
        )
        self.analysis_worker.progress_updated.connect(self.update_analysis_progress)
        self.analysis_worker.analysis_completed.connect(self.handle_analysis_results)
        self.analysis_worker.error_occurred.connect(self.handle_analysis_error)
        self.analysis_worker.start()
    
    def update_analysis_progress(self, value):
        """Analiz ilerlemesini güncelle"""
        self.progress_bar.setValue(value)
        
        progress_messages = {
            10: "Veriler işleniyor...",
            30: "Semptomlar analiz ediliyor...",
            50: "Risk faktörleri hesaplanıyor...",
            70: "Teşhis tahminleri yapılıyor...",
            90: "Öneriler oluşturuluyor...",
            100: "Analiz tamamlandı!"
        }
        
        if value in progress_messages:
            self.progress_label.setText(progress_messages[value])
            self.analysis_details.append(f"✓ {progress_messages[value]}")
    
    def handle_analysis_results(self, results):
        """Analiz sonuçlarını işle"""
        self.analysis_results = results
        
        # UI'yi sonuç moduna geçir
        self.start_analysis_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Analiz tamamlandı!")
        
        # Sonuçları göster
        self.display_results(results)
        
        # Rapor butonlarını aktif et
        self.generate_pdf_btn.setEnabled(True)
        self.generate_excel_btn.setEnabled(True)
        
        # Sonuçlar sekmesine geç
        self.tab_widget.setCurrentIndex(4)
        
        self.statusBar().showMessage("Analiz başarıyla tamamlandı!")
    
    def handle_analysis_error(self, error_message):
        """Analiz hatasını işle"""
        self.start_analysis_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Analiz hatası!")
        
        QMessageBox.critical(self, "Analiz Hatası", f"Analiz sırasında hata oluştu:\n{error_message}")
    
    def display_results(self, results):
        """Sonuçları göster"""
        # Özet
        summary = f"""
🏥 MYP Sağlık AI Analiz Raporu
📅 Tarih: {QDate.currentDate().toString('dd.MM.yyyy')}
👤 Hasta Profili: {self.age_spin.value()} yaş, {self.gender_combo.currentText()}

📊 GENEL DEĞERLENDİRME:
Risk Skoru: {results['risk_analysis'].get('total_score', 0):.1f}/10
Teşhis Güven Oranı: {results['diagnosis_prediction'].get('confidence', 0):.1f}%
        """
        self.results_summary.setPlainText(summary)
        
        # Risk analizi
        risk_text = self.format_risk_analysis(results['risk_analysis'])
        self.risk_results_text.setPlainText(risk_text)
        
        # Teşhis tahmini
        diagnosis_text = self.format_diagnosis_results(results['diagnosis_prediction'])
        self.diagnosis_results_text.setPlainText(diagnosis_text)
        
        # Öneriler
        recommendations_text = self.format_recommendations(results['recommendations'])
        self.recommendations_text.setPlainText(recommendations_text)
    
    def format_risk_analysis(self, risk_data):
        """Risk analizini formatla"""
        text = "⚠️ RİSK ANALİZİ RAPORU\n\n"
        
        if 'genetic_risk' in risk_data:
            text += f"🧬 Genetik Risk: {risk_data['genetic_risk']:.1f}/10\n"
        if 'lifestyle_risk' in risk_data:
            text += f"🏃‍♂️ Yaşam Tarzı Riski: {risk_data['lifestyle_risk']:.1f}/10\n"
        if 'symptom_risk' in risk_data:
            text += f"🩺 Semptom Riski: {risk_data['symptom_risk']:.1f}/10\n"
        
        text += f"\n📊 TOPLAM RİSK SKORU: {risk_data.get('total_score', 0):.1f}/10\n\n"
        
        # Risk kategorileri
        total_score = risk_data.get('total_score', 0)
        if total_score < 3:
            text += "✅ DÜŞÜK RİSK: Genel sağlık durumunuz iyi görünüyor.\n"
        elif total_score < 6:
            text += "⚠️ ORTA RİSK: Bazı risk faktörleri mevcut, dikkat edilmeli.\n"
        else:
            text += "🚨 YÜKSEK RİSK: Ciddi risk faktörleri var, doktor kontrolü öneriliyor.\n"
        
        return text
    
    def format_diagnosis_results(self, diagnosis_data):
        """Teşhis sonuçlarını formatla"""
        text = "🩺 TEŞHİS TAHMİN RAPORU\n\n"
        
        if 'primary_diagnosis' in diagnosis_data:
            text += f"🎯 Birincil Teşhis: {diagnosis_data['primary_diagnosis']}\n"
            text += f"📊 Güven Oranı: {diagnosis_data.get('confidence', 0):.1f}%\n\n"
        
        if 'differential_diagnosis' in diagnosis_data:
            text += "🔍 Ayırıcı Teşhisler:\n"
            for i, diag in enumerate(diagnosis_data['differential_diagnosis'][:5], 1):
                text += f"{i}. {diag.get('name', 'Bilinmeyen')} ({diag.get('probability', 0):.1f}%)\n"
        
        text += "\n⚠️ UYARI: Bu tahminler sadece bilgilendirme amaçlıdır. "
        text += "Kesin teşhis için mutlaka bir sağlık profesyoneline başvurun.\n"
        
        return text
    
    def format_recommendations(self, recommendations_data):
        """Önerileri formatla"""
        text = "💡 KİŞİSEL SAĞLIK ÖNERİLERİ\n\n"
        
        if 'immediate_actions' in recommendations_data:
            text += "🚨 ACİL ÖNERİLER:\n"
            for action in recommendations_data['immediate_actions']:
                text += f"• {action}\n"
            text += "\n"
        
        if 'lifestyle_recommendations' in recommendations_data:
            text += "🏃‍♂️ YAŞAM TARZI ÖNERİLERİ:\n"
            for rec in recommendations_data['lifestyle_recommendations']:
                text += f"• {rec}\n"
            text += "\n"
        
        if 'medical_recommendations' in recommendations_data:
            text += "🏥 TIBBİ ÖNERİLER:\n"
            for rec in recommendations_data['medical_recommendations']:
                text += f"• {rec}\n"
            text += "\n"
        
        if 'follow_up' in recommendations_data:
            text += "📅 TAKİP ÖNERİLERİ:\n"
            for follow in recommendations_data['follow_up']:
                text += f"• {follow}\n"
        
        text += "\n👨‍⚕️ Bu öneriler kişisel sağlık durumunuza göre hazırlanmıştır.\n"
        text += "Sağlık profesyoneli görüşü almayı unutmayın.\n"
        
        return text
    
    def generate_pdf_report(self):
        """PDF rapor oluştur"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapmanız gerekiyor!")
            return
        
        try:
            # Dosya kaydetme dialogu
            file_path, _ = QFileDialog.getSaveFileName(
                self, "PDF Rapor Kaydet", 
                f"MYP_Saglik_Raporu_{QDate.currentDate().toString('yyyyMMdd')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Yaşam tarzı verilerini topla
                lifestyle_data = self.collect_lifestyle_data()
                symptoms = self.symptoms_text.toPlainText()
                
                # PDF oluştur
                self.report_generator.generate_pdf_report(
                    self.analysis_results, lifestyle_data, symptoms, file_path
                )
                
                QMessageBox.information(self, "Başarılı", f"PDF rapor başarıyla oluşturuldu:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken hata oluştu:\n{str(e)}")
    
    def generate_excel_report(self):
        """Excel rapor oluştur"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapmanız gerekiyor!")
            return
        
        try:
            # Dosya kaydetme dialogu
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Excel Rapor Kaydet",
                f"MYP_Saglik_Raporu_{QDate.currentDate().toString('yyyyMMdd')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Yaşam tarzı verilerini topla
                lifestyle_data = self.collect_lifestyle_data()
                symptoms = self.symptoms_text.toPlainText()
                
                # Excel oluştur
                self.report_generator.generate_excel_report(
                    self.analysis_results, lifestyle_data, symptoms, file_path
                )
                
                QMessageBox.information(self, "Başarılı", f"Excel rapor başarıyla oluşturuldu:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel oluşturulurken hata oluştu:\n{str(e)}")