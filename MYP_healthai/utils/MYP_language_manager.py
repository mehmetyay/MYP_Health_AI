#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Dil Yönetimi Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LanguageManager:
    """Çok dilli destek için dil yönetimi sınıfı"""
    
    def __init__(self):
        self.current_language = 'tr'
        self.languages_dir = Path('data/languages')
        self.translations = {}
        self.supported_languages = ['tr', 'en', 'de', 'ku', 'ru']
        
        # Dil dosyalarını yükle
        self.load_all_languages()
    
    def load_all_languages(self):
        """Tüm dil dosyalarını yükle"""
        for lang_code in self.supported_languages:
            self.load_language(lang_code)
    
    def load_language(self, lang_code):
        """Belirli bir dil dosyasını yükle"""
        try:
            lang_file = self.languages_dir / f'{lang_code}.json'
            
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                logger.info(f"Dil dosyası yüklendi: {lang_code}")
            else:
                # Dil dosyası yoksa oluştur
                self.create_language_file(lang_code)
                
        except Exception as e:
            logger.error(f"Dil dosyası yükleme hatası ({lang_code}): {str(e)}")
    
    def create_language_file(self, lang_code):
        """Dil dosyası oluştur"""
        try:
            # Dil dosyası şablonları
            translations = self.get_language_template(lang_code)
            
            lang_file = self.languages_dir / f'{lang_code}.json'
            lang_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
            self.translations[lang_code] = translations
            logger.info(f"Dil dosyası oluşturuldu: {lang_code}")
            
        except Exception as e:
            logger.error(f"Dil dosyası oluşturma hatası ({lang_code}): {str(e)}")
    
    def get_language_template(self, lang_code):
        """Dil şablonunu al"""
        templates = {
            'tr': {
                # Ana Arayüz
                "app_title": "MYP Sağlık Yapay Zeka Sistemi",
                "app_subtitle": "Kişisel Sağlık Analizi ve Teşhis Sistemi",
                "developer": "Geliştirici: Mehmet Yay",
                "version": "Versiyon 1.0",
                
                # Menü ve Sekmeler
                "data_loading": "Veri Yükleme",
                "symptoms": "Semptomlar",
                "lifestyle": "Yaşam Tarzı",
                "analysis": "Analiz",
                "results": "Sonuçlar",
                
                # Veri Yükleme
                "load_genetic_data": "Genetik Veri Yükle",
                "load_medical_history": "Tıbbi Geçmiş Yükle",
                "load_family_history": "Aile Geçmişi Yükle",
                "data_preview": "Veri Önizlemesi",
                "file_loaded_successfully": "Dosya başarıyla yüklendi",
                "file_load_error": "Dosya yükleme hatası",
                
                # Semptomlar
                "symptom_description": "Yaşadığınız belirtileri detaylı olarak açıklayın:",
                "symptom_placeholder": "Örnek: Başım ağrıyor, yorgunluk hissediyorum, uykusuzluk yaşıyorum...",
                "quick_symptom_selection": "Hızlı Semptom Seçimi",
                "symptom_severity": "Genel Şiddet (1-10)",
                
                # Yaşam Tarzı
                "basic_info": "Temel Bilgiler",
                "age": "Yaş",
                "gender": "Cinsiyet",
                "height": "Boy (cm)",
                "weight": "Kilo (kg)",
                "male": "Erkek",
                "female": "Kadın",
                "other": "Diğer",
                
                "habits": "Alışkanlıklar",
                "smoking": "Sigara",
                "alcohol": "Alkol",
                "exercise": "Egzersiz (haftalık)",
                "sleep": "Günlük uyku (saat)",
                
                "smoking_never": "Hiç içmem",
                "smoking_quit": "Bıraktım",
                "smoking_occasional": "Ara sıra",
                "smoking_daily": "Günlük",
                
                "alcohol_never": "Hiç içmem",
                "alcohol_rarely": "Nadiren",
                "alcohol_weekly": "Haftalık",
                "alcohol_daily": "Günlük",
                
                "exercise_never": "Hiç",
                "exercise_1_2": "1-2 gün",
                "exercise_3_4": "3-4 gün",
                "exercise_5_plus": "5+ gün",
                
                # Analiz
                "analysis_control": "Analiz Kontrolü",
                "analysis_type": "Analiz Türü",
                "comprehensive_analysis": "Kapsamlı Analiz",
                "quick_assessment": "Hızlı Değerlendirme",
                "risk_analysis": "Risk Analizi",
                "symptom_focused": "Semptom Odaklı",
                "start_analysis": "ANALİZİ BAŞLAT",
                "analysis_progress": "Analiz İlerlemesi",
                "analysis_waiting": "Analiz bekleniyor...",
                "analysis_completed": "Analiz tamamlandı!",
                
                # Sonuçlar
                "analysis_summary": "Analiz Özeti",
                "risk_analysis_results": "Risk Analizi",
                "diagnosis_prediction": "Teşhis Tahmini",
                "recommendations": "Öneriler",
                "generate_pdf_report": "PDF Rapor Oluştur",
                "generate_excel_report": "Excel Rapor Oluştur",
                
                # Mesajlar
                "warning": "Uyarı",
                "error": "Hata",
                "success": "Başarılı",
                "info": "Bilgi",
                "load_data_first": "Lütfen önce veri dosyalarını yükleyin!",
                "enter_symptoms": "Lütfen semptomlarınızı girin!",
                "analysis_required": "Önce analiz yapmanız gerekiyor!",
                
                # Risk Seviyeleri
                "low_risk": "Düşük Risk",
                "medium_risk": "Orta Risk",
                "high_risk": "Yüksek Risk",
                
                # Genel
                "yes": "Evet",
                "no": "Hayır",
                "unknown": "Bilinmeyen",
                "save": "Kaydet",
                "cancel": "İptal",
                "close": "Kapat",
                "ok": "Tamam"
            },
            
            'en': {
                # Main Interface
                "app_title": "MYP Health AI System",
                "app_subtitle": "Personal Health Analysis and Diagnosis System",
                "developer": "Developer: Mehmet Yay",
                "version": "Version 1.0",
                
                # Menu and Tabs
                "data_loading": "Data Loading",
                "symptoms": "Symptoms",
                "lifestyle": "Lifestyle",
                "analysis": "Analysis",
                "results": "Results",
                
                # Data Loading
                "load_genetic_data": "Load Genetic Data",
                "load_medical_history": "Load Medical History",
                "load_family_history": "Load Family History",
                "data_preview": "Data Preview",
                "file_loaded_successfully": "File loaded successfully",
                "file_load_error": "File loading error",
                
                # Symptoms
                "symptom_description": "Describe your symptoms in detail:",
                "symptom_placeholder": "Example: I have a headache, feeling tired, experiencing insomnia...",
                "quick_symptom_selection": "Quick Symptom Selection",
                "symptom_severity": "General Severity (1-10)",
                
                # Lifestyle
                "basic_info": "Basic Information",
                "age": "Age",
                "gender": "Gender",
                "height": "Height (cm)",
                "weight": "Weight (kg)",
                "male": "Male",
                "female": "Female",
                "other": "Other",
                
                "habits": "Habits",
                "smoking": "Smoking",
                "alcohol": "Alcohol",
                "exercise": "Exercise (weekly)",
                "sleep": "Daily sleep (hours)",
                
                "smoking_never": "Never smoke",
                "smoking_quit": "Quit",
                "smoking_occasional": "Occasionally",
                "smoking_daily": "Daily",
                
                "alcohol_never": "Never drink",
                "alcohol_rarely": "Rarely",
                "alcohol_weekly": "Weekly",
                "alcohol_daily": "Daily",
                
                "exercise_never": "Never",
                "exercise_1_2": "1-2 days",
                "exercise_3_4": "3-4 days",
                "exercise_5_plus": "5+ days",
                
                # Analysis
                "analysis_control": "Analysis Control",
                "analysis_type": "Analysis Type",
                "comprehensive_analysis": "Comprehensive Analysis",
                "quick_assessment": "Quick Assessment",
                "risk_analysis": "Risk Analysis",
                "symptom_focused": "Symptom Focused",
                "start_analysis": "START ANALYSIS",
                "analysis_progress": "Analysis Progress",
                "analysis_waiting": "Waiting for analysis...",
                "analysis_completed": "Analysis completed!",
                
                # Results
                "analysis_summary": "Analysis Summary",
                "risk_analysis_results": "Risk Analysis",
                "diagnosis_prediction": "Diagnosis Prediction",
                "recommendations": "Recommendations",
                "generate_pdf_report": "Generate PDF Report",
                "generate_excel_report": "Generate Excel Report",
                
                # Messages
                "warning": "Warning",
                "error": "Error",
                "success": "Success",
                "info": "Information",
                "load_data_first": "Please load data files first!",
                "enter_symptoms": "Please enter your symptoms!",
                "analysis_required": "Analysis required first!",
                
                # Risk Levels
                "low_risk": "Low Risk",
                "medium_risk": "Medium Risk",
                "high_risk": "High Risk",
                
                # General
                "yes": "Yes",
                "no": "No",
                "unknown": "Unknown",
                "save": "Save",
                "cancel": "Cancel",
                "close": "Close",
                "ok": "OK"
            },
            
            'de': {
                # Hauptschnittstelle
                "app_title": "MYP Gesundheits-KI-System",
                "app_subtitle": "Persönliches Gesundheitsanalyse- und Diagnosesystem",
                "developer": "Entwickler: Mehmet Yay",
                "version": "Version 1.0",
                
                # Menü und Registerkarten
                "data_loading": "Daten laden",
                "symptoms": "Symptome",
                "lifestyle": "Lebensstil",
                "analysis": "Analyse",
                "results": "Ergebnisse",
                
                # Daten laden
                "load_genetic_data": "Genetische Daten laden",
                "load_medical_history": "Krankengeschichte laden",
                "load_family_history": "Familiengeschichte laden",
                "data_preview": "Datenvorschau",
                "file_loaded_successfully": "Datei erfolgreich geladen",
                "file_load_error": "Fehler beim Laden der Datei",
                
                # Symptome
                "symptom_description": "Beschreiben Sie Ihre Symptome detailliert:",
                "symptom_placeholder": "Beispiel: Ich habe Kopfschmerzen, fühle mich müde, leide unter Schlaflosigkeit...",
                "quick_symptom_selection": "Schnelle Symptomauswahl",
                "symptom_severity": "Allgemeine Schwere (1-10)",
                
                # Lebensstil
                "basic_info": "Grundinformationen",
                "age": "Alter",
                "gender": "Geschlecht",
                "height": "Größe (cm)",
                "weight": "Gewicht (kg)",
                "male": "Männlich",
                "female": "Weiblich",
                "other": "Andere",
                
                "habits": "Gewohnheiten",
                "smoking": "Rauchen",
                "alcohol": "Alkohol",
                "exercise": "Sport (wöchentlich)",
                "sleep": "Täglicher Schlaf (Stunden)",
                
                "smoking_never": "Rauche nie",
                "smoking_quit": "Aufgehört",
                "smoking_occasional": "Gelegentlich",
                "smoking_daily": "Täglich",
                
                "alcohol_never": "Trinke nie",
                "alcohol_rarely": "Selten",
                "alcohol_weekly": "Wöchentlich",
                "alcohol_daily": "Täglich",
                
                "exercise_never": "Nie",
                "exercise_1_2": "1-2 Tage",
                "exercise_3_4": "3-4 Tage",
                "exercise_5_plus": "5+ Tage",
                
                # Analyse
                "analysis_control": "Analysekontrolle",
                "analysis_type": "Analysetyp",
                "comprehensive_analysis": "Umfassende Analyse",
                "quick_assessment": "Schnelle Bewertung",
                "risk_analysis": "Risikoanalyse",
                "symptom_focused": "Symptomorientiert",
                "start_analysis": "ANALYSE STARTEN",
                "analysis_progress": "Analysefortschritt",
                "analysis_waiting": "Warten auf Analyse...",
                "analysis_completed": "Analyse abgeschlossen!",
                
                # Ergebnisse
                "analysis_summary": "Analysezusammenfassung",
                "risk_analysis_results": "Risikoanalyse",
                "diagnosis_prediction": "Diagnoseprognose",
                "recommendations": "Empfehlungen",
                "generate_pdf_report": "PDF-Bericht erstellen",
                "generate_excel_report": "Excel-Bericht erstellen",
                
                # Nachrichten
                "warning": "Warnung",
                "error": "Fehler",
                "success": "Erfolg",
                "info": "Information",
                "load_data_first": "Bitte laden Sie zuerst Datendateien!",
                "enter_symptoms": "Bitte geben Sie Ihre Symptome ein!",
                "analysis_required": "Analyse zuerst erforderlich!",
                
                # Risikostufen
                "low_risk": "Niedriges Risiko",
                "medium_risk": "Mittleres Risiko",
                "high_risk": "Hohes Risiko",
                
                # Allgemein
                "yes": "Ja",
                "no": "Nein",
                "unknown": "Unbekannt",
                "save": "Speichern",
                "cancel": "Abbrechen",
                "close": "Schließen",
                "ok": "OK"
            },
            
            'ku': {
                # Navenda Sereke
                "app_title": "Sîstema AI ya Tendurustiyê ya MYP",
                "app_subtitle": "Sîstema Analîza Tendurustiya Kesane û Teşhîsê",
                "developer": "Pêşdebirkar: Mehmet Yay",
                "version": "Guherto 1.0",
                
                # Menu û Taban
                "data_loading": "Barkirina Daneyan",
                "symptoms": "Nîşan",
                "lifestyle": "Jiyana Rojane",
                "analysis": "Analîz",
                "results": "Encam",
                
                # Barkirina Daneyan
                "load_genetic_data": "Daneyên Genetîk Bar bike",
                "load_medical_history": "Dîroka Bijîşkî Bar bike",
                "load_family_history": "Dîroka Malbatê Bar bike",
                "data_preview": "Pêşdîtina Daneyan",
                "file_loaded_successfully": "Pel bi serkeftî hate barkirin",
                "file_load_error": "Xeletiya barkirina pelê",
                
                # Nîşan
                "symptom_description": "Nîşanên xwe bi hûrgulî rave bikin:",
                "symptom_placeholder": "Mînak: Serê min êş dike, westiyayî hîs dikim, nexewtin heye...",
                "quick_symptom_selection": "Hilbijartina Nîşanên Bilez",
                "symptom_severity": "Girtiya Giştî (1-10)",
                
                # Jiyana Rojane
                "basic_info": "Agahiyên Bingehîn",
                "age": "Temen",
                "gender": "Zayend",
                "height": "Bilindî (cm)",
                "weight": "Giran (kg)",
                "male": "Mêr",
                "female": "Jin",
                "other": "Yên din",
                
                "habits": "Adet",
                "smoking": "Cixare",
                "alcohol": "Alkol",
                "exercise": "Werzîş (heftewar)",
                "sleep": "Xewa rojane (saet)",
                
                "smoking_never": "Tu car naxim",
                "smoking_quit": "Berda",
                "smoking_occasional": "Carna carna",
                "smoking_daily": "Rojane",
                
                "alcohol_never": "Tu car navêjim",
                "alcohol_rarely": "Kêm",
                "alcohol_weekly": "Heftewar",
                "alcohol_daily": "Rojane",
                
                "exercise_never": "Tu car",
                "exercise_1_2": "1-2 roj",
                "exercise_3_4": "3-4 roj",
                "exercise_5_plus": "5+ roj",
                
                # Analîz
                "analysis_control": "Kontrola Analîzê",
                "analysis_type": "Cureyê Analîzê",
                "comprehensive_analysis": "Analîza Berfireh",
                "quick_assessment": "Nirxandina Bilez",
                "risk_analysis": "Analîza Xetereyê",
                "symptom_focused": "Li ser Nîşanan",
                "start_analysis": "ANALÎZÊ DEST PÊ BIKE",
                "analysis_progress": "Pêşketina Analîzê",
                "analysis_waiting": "Li benda analîzê...",
                "analysis_completed": "Analîz temam bû!",
                
                # Encam
                "analysis_summary": "Kurteya Analîzê",
                "risk_analysis_results": "Analîza Xetereyê",
                "diagnosis_prediction": "Pêşbîniya Teşhîsê",
                "recommendations": "Pêşniyar",
                "generate_pdf_report": "Rappora PDF Çê bike",
                "generate_excel_report": "Rappora Excel Çê bike",
                
                # Peyam
                "warning": "Hişyarî",
                "error": "Xeletî",
                "success": "Serkeftin",
                "info": "Agahî",
                "load_data_first": "Ji kerema xwe pêşî pelên daneyan bar bikin!",
                "enter_symptoms": "Ji kerema xwe nîşanên xwe binivîsin!",
                "analysis_required": "Pêşî analîz hewce ye!",
                
                # Astên Xetereyê
                "low_risk": "Xeterey Kêm",
                "medium_risk": "Xeterey Navîn",
                "high_risk": "Xeterey Zêde",
                
                # Giştî
                "yes": "Erê",
                "no": "Na",
                "unknown": "Nenas",
                "save": "Tomar bike",
                "cancel": "Betal bike",
                "close": "Bigire",
                "ok": "Baş e"
            },
            
            'ru': {
                # Главный интерфейс
                "app_title": "Система ИИ Здоровья MYP",
                "app_subtitle": "Система персонального анализа здоровья и диагностики",
                "developer": "Разработчик: Мехмет Яй",
                "version": "Версия 1.0",
                
                # Меню и вкладки
                "data_loading": "Загрузка данных",
                "symptoms": "Симптомы",
                "lifestyle": "Образ жизни",
                "analysis": "Анализ",
                "results": "Результаты",
                
                # Загрузка данных
                "load_genetic_data": "Загрузить генетические данные",
                "load_medical_history": "Загрузить медицинскую историю",
                "load_family_history": "Загрузить семейную историю",
                "data_preview": "Предварительный просмотр данных",
                "file_loaded_successfully": "Файл успешно загружен",
                "file_load_error": "Ошибка загрузки файла",
                
                # Симптомы
                "symptom_description": "Опишите ваши симптомы подробно:",
                "symptom_placeholder": "Пример: У меня болит голова, чувствую усталость, бессонница...",
                "quick_symptom_selection": "Быстрый выбор симптомов",
                "symptom_severity": "Общая тяжесть (1-10)",
                
                # Образ жизни
                "basic_info": "Основная информация",
                "age": "Возраст",
                "gender": "Пол",
                "height": "Рост (см)",
                "weight": "Вес (кг)",
                "male": "Мужской",
                "female": "Женский",
                "other": "Другой",
                
                "habits": "Привычки",
                "smoking": "Курение",
                "alcohol": "Алкоголь",
                "exercise": "Упражнения (еженедельно)",
                "sleep": "Ежедневный сон (часы)",
                
                "smoking_never": "Никогда не курю",
                "smoking_quit": "Бросил",
                "smoking_occasional": "Иногда",
                "smoking_daily": "Ежедневно",
                
                "alcohol_never": "Никогда не пью",
                "alcohol_rarely": "Редко",
                "alcohol_weekly": "Еженедельно",
                "alcohol_daily": "Ежедневно",
                
                "exercise_never": "Никогда",
                "exercise_1_2": "1-2 дня",
                "exercise_3_4": "3-4 дня",
                "exercise_5_plus": "5+ дней",
                
                # Анализ
                "analysis_control": "Управление анализом",
                "analysis_type": "Тип анализа",
                "comprehensive_analysis": "Комплексный анализ",
                "quick_assessment": "Быстрая оценка",
                "risk_analysis": "Анализ рисков",
                "symptom_focused": "Фокус на симптомах",
                "start_analysis": "НАЧАТЬ АНАЛИЗ",
                "analysis_progress": "Прогресс анализа",
                "analysis_waiting": "Ожидание анализа...",
                "analysis_completed": "Анализ завершен!",
                
                # Результаты
                "analysis_summary": "Сводка анализа",
                "risk_analysis_results": "Анализ рисков",
                "diagnosis_prediction": "Прогноз диагноза",
                "recommendations": "Рекомендации",
                "generate_pdf_report": "Создать PDF отчет",
                "generate_excel_report": "Создать Excel отчет",
                
                # Сообщения
                "warning": "Предупреждение",
                "error": "Ошибка",
                "success": "Успех",
                "info": "Информация",
                "load_data_first": "Пожалуйста, сначала загрузите файлы данных!",
                "enter_symptoms": "Пожалуйста, введите ваши симптомы!",
                "analysis_required": "Сначала требуется анализ!",
                
                # Уровни риска
                "low_risk": "Низкий риск",
                "medium_risk": "Средний риск",
                "high_risk": "Высокий риск",
                
                # Общее
                "yes": "Да",
                "no": "Нет",
                "unknown": "Неизвестно",
                "save": "Сохранить",
                "cancel": "Отмена",
                "close": "Закрыть",
                "ok": "ОК"
            }
        }
        
        return templates.get(lang_code, templates['tr'])
    
    def set_language(self, lang_code):
        """Aktif dili ayarla"""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            logger.info(f"Dil değiştirildi: {lang_code}")
        else:
            logger.warning(f"Desteklenmeyen dil kodu: {lang_code}")
    
    def get_text(self, key, default=None):
        """Çeviri metnini al"""
        try:
            if self.current_language in self.translations:
                text = self.translations[self.current_language].get(key, default or key)
                return text
            else:
                return default or key
        except Exception as e:
            logger.error(f"Çeviri alma hatası: {str(e)}")
            return default or key
    
    def get_current_language(self):
        """Aktif dili al"""
        return self.current_language
    
    def get_supported_languages(self):
        """Desteklenen dilleri al"""
        return self.supported_languages
    
    def get_language_name(self, lang_code):
        """Dil koduna göre dil adını al"""
        language_names = {
            'tr': 'Türkçe',
            'en': 'English',
            'de': 'Deutsch',
            'ku': 'Kurdî',
            'ru': 'Русский'
        }
        return language_names.get(lang_code, lang_code)
    
    def update_translation(self, key, value, lang_code=None):
        """Çeviri güncelle"""
        try:
            target_lang = lang_code or self.current_language
            
            if target_lang not in self.translations:
                self.translations[target_lang] = {}
            
            self.translations[target_lang][key] = value
            
            # Dosyaya kaydet
            self.save_language_file(target_lang)
            
            logger.info(f"Çeviri güncellendi: {key} ({target_lang})")
            
        except Exception as e:
            logger.error(f"Çeviri güncelleme hatası: {str(e)}")
    
    def save_language_file(self, lang_code):
        """Dil dosyasını kaydet"""
        try:
            if lang_code in self.translations:
                lang_file = self.languages_dir / f'{lang_code}.json'
                
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(self.translations[lang_code], f, ensure_ascii=False, indent=2)
                
                logger.info(f"Dil dosyası kaydedildi: {lang_code}")
                
        except Exception as e:
            logger.error(f"Dil dosyası kaydetme hatası ({lang_code}): {str(e)}")
    
    def export_translations(self, output_path):
        """Tüm çevirileri dışa aktar"""
        try:
            export_data = {
                'metadata': {
                    'version': '1.0',
                    'languages': self.supported_languages,
                    'current_language': self.current_language,
                    'export_date': str(Path(__file__).stat().st_mtime)
                },
                'translations': self.translations
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Çeviriler dışa aktarıldı: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Çeviri dışa aktarma hatası: {str(e)}")
            return False
    
    def import_translations(self, input_path):
        """Çevirileri içe aktar"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'translations' in import_data:
                self.translations.update(import_data['translations'])
                
                # Tüm dil dosyalarını güncelle
                for lang_code in self.translations.keys():
                    self.save_language_file(lang_code)
                
                logger.info(f"Çeviriler içe aktarıldı: {input_path}")
                return True
            else:
                logger.error("Geçersiz çeviri dosyası formatı")
                return False
                
        except Exception as e:
            logger.error(f"Çeviri içe aktarma hatası: {str(e)}")
            return False