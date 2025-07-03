#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Rapor Oluşturma Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """PDF ve Excel rapor oluşturma sınıfı"""
    
    def __init__(self):
        self.setup_fonts()
        self.styles = self.create_styles()
        
    def setup_fonts(self):
        """Font ayarlarını yap"""
        try:
            # Türkçe karakter desteği için font ekle
            # Not: Gerçek uygulamada font dosyalarını assets/fonts/ klasörüne koyun
            pass
        except Exception as e:
            logger.warning(f"Font yükleme uyarısı: {str(e)}")
    
    def create_styles(self):
        """Rapor stilleri oluştur"""
        styles = getSampleStyleSheet()
        
        # Özel stiller ekle
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        ))
        
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_RIGHT,
            textColor=colors.grey
        ))
        
        return styles
    
    def generate_pdf_report(self, analysis_results, lifestyle_data, symptoms, output_path):
        """PDF rapor oluştur"""
        try:
            logger.info("PDF rapor oluşturuluyor...")
            
            # PDF dokümanı oluştur
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Rapor içeriğini oluştur
            story = []
            
            # Başlık sayfası
            self.add_title_page(story, lifestyle_data)
            
            # Özet bölümü
            self.add_summary_section(story, analysis_results, lifestyle_data)
            
            # Risk analizi bölümü
            self.add_risk_analysis_section(story, analysis_results['risk_analysis'])
            
            # Semptom analizi bölümü
            self.add_symptom_analysis_section(story, analysis_results['symptom_analysis'], symptoms)
            
            # Teşhis tahmini bölümü
            self.add_diagnosis_section(story, analysis_results['diagnosis_prediction'])
            
            # Öneriler bölümü
            self.add_recommendations_section(story, analysis_results['recommendations'])
            
            # Yaşam tarzı analizi bölümü
            self.add_lifestyle_analysis_section(story, lifestyle_data)
            
            # Disclaimer bölümü
            self.add_disclaimer_section(story)
            
            # PDF'i oluştur
            doc.build(story)
            
            logger.info(f"PDF rapor oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF rapor oluşturma hatası: {str(e)}")
            return False
    
    def add_title_page(self, story, lifestyle_data):
        """Başlık sayfası ekle"""
        # Ana başlık
        title = Paragraph("🏥 MYP Sağlık Yapay Zeka Analizi", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Alt başlık
        subtitle = Paragraph("Kişisel Sağlık Değerlendirme Raporu", self.styles['Heading2'])
        story.append(subtitle)
        story.append(Spacer(1, 30))
        
        # Hasta bilgileri tablosu
        patient_data = [
            ['Rapor Tarihi:', datetime.now().strftime('%d.%m.%Y %H:%M')],
            ['Hasta Yaşı:', f"{lifestyle_data.get('age', 'Belirtilmemiş')} yaş"],
            ['Cinsiyet:', lifestyle_data.get('gender', 'Belirtilmemiş')],
            ['Boy:', f"{lifestyle_data.get('height', 'Belirtilmemiş')} cm"],
            ['Kilo:', f"{lifestyle_data.get('weight', 'Belirtilmemiş')} kg"],
        ]
        
        # BMI hesapla
        if lifestyle_data.get('height') and lifestyle_data.get('weight'):
            height_m = lifestyle_data['height'] / 100
            bmi = lifestyle_data['weight'] / (height_m ** 2)
            patient_data.append(['BMI:', f"{bmi:.1f}"])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 30))
        
        # Geliştirici bilgisi
        developer_info = Paragraph(
            "Bu rapor Mehmet Yay tarafından geliştirilen MYP Sağlık AI sistemi tarafından oluşturulmuştur.<br/>"
            "Tüm hakları saklıdır. © 2025 Mehmet Yay",
            self.styles['RightAlign']
        )
        story.append(developer_info)
        story.append(PageBreak())
    
    def add_summary_section(self, story, analysis_results, lifestyle_data):
        """Özet bölümü ekle"""
        story.append(Paragraph("📋 GENEL ÖZET", self.styles['CustomHeading']))
        
        # Risk skoru
        risk_score = analysis_results['risk_analysis'].get('total_score', 0)
        risk_category = analysis_results['risk_analysis'].get('risk_category', 'Bilinmeyen')
        
        summary_text = f"""
        <b>Genel Risk Skoru:</b> {risk_score:.1f}/10 ({risk_category} Risk)<br/>
        <b>Birincil Teşhis Tahmini:</b> {analysis_results['diagnosis_prediction'].get('primary_diagnosis', 'Belirsiz')}<br/>
        <b>Güven Oranı:</b> {analysis_results['diagnosis_prediction'].get('confidence', 0):.1f}%<br/>
        <b>Tespit Edilen Semptom Sayısı:</b> {len(analysis_results['symptom_analysis'].get('detected_symptoms', []))}<br/>
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Hızlı öneriler
        immediate_actions = analysis_results['recommendations'].get('immediate_actions', [])
        if immediate_actions:
            story.append(Paragraph("🚨 ACİL ÖNERİLER:", self.styles['CustomHeading']))
            for action in immediate_actions[:3]:  # İlk 3 öneri
                story.append(Paragraph(f"• {action}", self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
    
    def add_risk_analysis_section(self, story, risk_analysis):
        """Risk analizi bölümü ekle"""
        story.append(Paragraph("⚠️ RİSK ANALİZİ", self.styles['CustomHeading']))
        
        # Risk skorları tablosu
        risk_data = [
            ['Risk Faktörü', 'Skor', 'Değerlendirme']
        ]
        
        if 'genetic_risk' in risk_analysis:
            risk_data.append(['Genetik Risk', f"{risk_analysis['genetic_risk']:.1f}/10", self.get_risk_evaluation(risk_analysis['genetic_risk'])])
        
        if 'lifestyle_risk' in risk_analysis:
            risk_data.append(['Yaşam Tarzı Riski', f"{risk_analysis['lifestyle_risk']:.1f}/10", self.get_risk_evaluation(risk_analysis['lifestyle_risk'])])
        
        if 'medical_history_risk' in risk_analysis:
            risk_data.append(['Tıbbi Geçmiş Riski', f"{risk_analysis['medical_history_risk']:.1f}/10", self.get_risk_evaluation(risk_analysis['medical_history_risk'])])
        
        if 'family_history_risk' in risk_analysis:
            risk_data.append(['Aile Geçmişi Riski', f"{risk_analysis['family_history_risk']:.1f}/10", self.get_risk_evaluation(risk_analysis['family_history_risk'])])
        
        risk_data.append(['TOPLAM RİSK', f"{risk_analysis.get('total_score', 0):.1f}/10", risk_analysis.get('risk_category', 'Bilinmeyen')])
        
        risk_table = Table(risk_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 20))
    
    def add_symptom_analysis_section(self, story, symptom_analysis, symptoms):
        """Semptom analizi bölümü ekle"""
        story.append(Paragraph("🩺 SEMPTOM ANALİZİ", self.styles['CustomHeading']))
        
        # Girilen semptomlar
        story.append(Paragraph("<b>Bildirilen Semptomlar:</b>", self.styles['CustomNormal']))
        story.append(Paragraph(symptoms, self.styles['CustomNormal']))
        story.append(Spacer(1, 10))
        
        # Tespit edilen semptomlar
        detected_symptoms = symptom_analysis.get('detected_symptoms', [])
        if detected_symptoms:
            story.append(Paragraph(f"<b>Tespit Edilen Semptomlar ({len(detected_symptoms)} adet):</b>", self.styles['CustomNormal']))
            for symptom in detected_symptoms:
                story.append(Paragraph(f"• {symptom}", self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        # Sistem analizi
        system_analysis = symptom_analysis.get('system_analysis', {})
        if system_analysis:
            story.append(Paragraph("<b>Sistem Bazlı Analiz:</b>", self.styles['CustomNormal']))
            
            system_data = [['Sistem', 'Eşleşen Semptom', 'Toplam Semptom', 'Oran']]
            
            for system, data in system_analysis.items():
                system_data.append([
                    system.title(),
                    str(data['matches']),
                    str(data['total']),
                    f"{data['ratio']*100:.1f}%"
                ])
            
            system_table = Table(system_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
            system_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(system_table)
        
        story.append(Spacer(1, 20))
    
    def add_diagnosis_section(self, story, diagnosis_prediction):
        """Teşhis bölümü ekle"""
        story.append(Paragraph("🎯 TEŞHİS TAHMİNİ", self.styles['CustomHeading']))
        
        # Birincil teşhis
        primary_diagnosis = diagnosis_prediction.get('primary_diagnosis', 'Belirsiz')
        confidence = diagnosis_prediction.get('confidence', 0)
        
        diagnosis_text = f"""
        <b>Birincil Teşhis:</b> {primary_diagnosis}<br/>
        <b>Güven Oranı:</b> {confidence:.1f}%<br/>
        <b>ICD-10 Kodu:</b> {diagnosis_prediction.get('icd10_code', 'Bilinmeyen')}<br/>
        """
        
        story.append(Paragraph(diagnosis_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 10))
        
        # Ayırıcı teşhisler
        differential_diagnosis = diagnosis_prediction.get('differential_diagnosis', [])
        if differential_diagnosis:
            story.append(Paragraph("<b>Ayırıcı Teşhisler:</b>", self.styles['CustomNormal']))
            
            diff_data = [['Sıra', 'Teşhis', 'Olasılık']]
            
            for i, diag in enumerate(differential_diagnosis[:5], 1):
                diff_data.append([
                    str(i),
                    diag.get('name', 'Bilinmeyen'),
                    f"{diag.get('probability', 0):.1f}%"
                ])
            
            diff_table = Table(diff_data, colWidths=[0.5*inch, 3*inch, 1*inch])
            diff_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(diff_table)
        
        story.append(Spacer(1, 20))
    
    def add_recommendations_section(self, story, recommendations):
        """Öneriler bölümü ekle"""
        story.append(Paragraph("💡 KİŞİSEL ÖNERİLER", self.styles['CustomHeading']))
        
        # Acil öneriler
        immediate_actions = recommendations.get('immediate_actions', [])
        if immediate_actions:
            story.append(Paragraph("🚨 Acil Öneriler:", self.styles['Heading3']))
            for action in immediate_actions:
                story.append(Paragraph(f"• {action}", self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        # Yaşam tarzı önerileri
        lifestyle_recommendations = recommendations.get('lifestyle_recommendations', [])
        if lifestyle_recommendations:
            story.append(Paragraph("🏃‍♂️ Yaşam Tarzı Önerileri:", self.styles['Heading3']))
            for rec in lifestyle_recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        # Tıbbi öneriler
        medical_recommendations = recommendations.get('medical_recommendations', [])
        if medical_recommendations:
            story.append(Paragraph("🏥 Tıbbi Öneriler:", self.styles['Heading3']))
            for rec in medical_recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        # Takip önerileri
        follow_up = recommendations.get('follow_up', [])
        if follow_up:
            story.append(Paragraph("📅 Takip Önerileri:", self.styles['Heading3']))
            for follow in follow_up:
                story.append(Paragraph(f"• {follow}", self.styles['CustomNormal']))
        
        story.append(Spacer(1, 20))
    
    def add_lifestyle_analysis_section(self, story, lifestyle_data):
        """Yaşam tarzı analizi bölümü ekle"""
        story.append(Paragraph("🏃‍♂️ YAŞAM TARZI ANALİZİ", self.styles['CustomHeading']))
        
        # Yaşam tarzı faktörleri tablosu
        lifestyle_factors = [
            ['Faktör', 'Mevcut Durum', 'Değerlendirme']
        ]
        
        # Sigara
        smoking = lifestyle_data.get('smoking', 'Belirtilmemiş')
        smoking_eval = self.evaluate_smoking(smoking)
        lifestyle_factors.append(['Sigara Kullanımı', smoking, smoking_eval])
        
        # Alkol
        alcohol = lifestyle_data.get('alcohol', 'Belirtilmemiş')
        alcohol_eval = self.evaluate_alcohol(alcohol)
        lifestyle_factors.append(['Alkol Kullanımı', alcohol, alcohol_eval])
        
        # Egzersiz
        exercise = lifestyle_data.get('exercise', 'Belirtilmemiş')
        exercise_eval = self.evaluate_exercise(exercise)
        lifestyle_factors.append(['Egzersiz Sıklığı', exercise, exercise_eval])
        
        # Uyku
        sleep_hours = lifestyle_data.get('sleep_hours', 'Belirtilmemiş')
        sleep_eval = self.evaluate_sleep(sleep_hours)
        lifestyle_factors.append(['Günlük Uyku', f"{sleep_hours} saat" if isinstance(sleep_hours, (int, float)) else sleep_hours, sleep_eval])
        
        # Stres
        stress_level = lifestyle_data.get('stress_level', 'Belirtilmemiş')
        stress_eval = self.evaluate_stress(stress_level)
        lifestyle_factors.append(['Stres Seviyesi', f"{stress_level}/10" if isinstance(stress_level, (int, float)) else stress_level, stress_eval])
        
        lifestyle_table = Table(lifestyle_factors, colWidths=[2*inch, 1.5*inch, 2*inch])
        lifestyle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(lifestyle_table)
        story.append(Spacer(1, 20))
    
    def add_disclaimer_section(self, story):
        """Sorumluluk reddi bölümü ekle"""
        story.append(PageBreak())
        story.append(Paragraph("⚠️ SORUMLULUK REDDİ VE UYARILAR", self.styles['CustomHeading']))
        
        disclaimer_text = """
        <b>ÖNEMLİ UYARI:</b><br/><br/>
        
        Bu rapor, MYP Sağlık Yapay Zeka sistemi tarafından oluşturulan bir değerlendirmedir ve 
        sadece bilgilendirme amaçlıdır. Bu rapor:<br/><br/>
        
        • Tıbbi teşhis yerine geçmez<br/>
        • Doktor muayenesi ve profesyonel tıbbi görüş gerektiren durumları ortadan kaldırmaz<br/>
        • Kesin teşhis için mutlaka bir sağlık profesyoneline başvurulmalıdır<br/>
        • Acil durumlarda derhal en yakın sağlık kuruluşuna başvurun<br/>
        • İlaç kullanımı ve tedavi kararları için doktor onayı alın<br/><br/>
        
        <b>Geliştirici Bilgileri:</b><br/>
        Bu yazılım Mehmet Yay tarafından geliştirilmiştir.<br/>
        Tüm hakları saklıdır. © 2025 Mehmet Yay<br/>
        İzinsiz kopyalanamaz, dağıtılamaz, satılamaz.<br/><br/>
        
        <b>Veri Gizliliği:</b><br/>
        Tüm verileriniz yerel olarak işlenir ve dışarıya aktarılmaz.<br/>
        Kişisel sağlık bilgileriniz güvenlik altındadır.<br/><br/>
        
        <b>Rapor Tarihi:</b> {}<br/>
        <b>Sistem Versiyonu:</b> MYP Sağlık AI v1.0
        """.format(datetime.now().strftime('%d.%m.%Y %H:%M'))
        
        story.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))
    
    def get_risk_evaluation(self, risk_score):
        """Risk skoruna göre değerlendirme"""
        if risk_score < 3:
            return "Düşük"
        elif risk_score < 6:
            return "Orta"
        else:
            return "Yüksek"
    
    def evaluate_smoking(self, smoking):
        """Sigara kullanımını değerlendir"""
        evaluations = {
            'Hiç içmem': 'Mükemmel',
            'Bıraktım': 'İyi',
            'Ara sıra': 'Dikkat',
            'Günlük': 'Risk'
        }
        return evaluations.get(smoking, 'Bilinmeyen')
    
    def evaluate_alcohol(self, alcohol):
        """Alkol kullanımını değerlendir"""
        evaluations = {
            'Hiç içmem': 'Mükemmel',
            'Nadiren': 'İyi',
            'Haftalık': 'Dikkat',
            'Günlük': 'Risk'
        }
        return evaluations.get(alcohol, 'Bilinmeyen')
    
    def evaluate_exercise(self, exercise):
        """Egzersiz sıklığını değerlendir"""
        evaluations = {
            'Hiç': 'Yetersiz',
            '1-2 gün': 'Az',
            '3-4 gün': 'İyi',
            '5+ gün': 'Mükemmel'
        }
        return evaluations.get(exercise, 'Bilinmeyen')
    
    def evaluate_sleep(self, sleep_hours):
        """Uyku süresini değerlendir"""
        if isinstance(sleep_hours, (int, float)):
            if sleep_hours < 6:
                return 'Yetersiz'
            elif sleep_hours <= 9:
                return 'İyi'
            else:
                return 'Fazla'
        return 'Bilinmeyen'
    
    def evaluate_stress(self, stress_level):
        """Stres seviyesini değerlendir"""
        if isinstance(stress_level, (int, float)):
            if stress_level <= 3:
                return 'Düşük'
            elif stress_level <= 6:
                return 'Orta'
            else:
                return 'Yüksek'
        return 'Bilinmeyen'
    
    def generate_excel_report(self, analysis_results, lifestyle_data, symptoms, output_path):
        """Excel rapor oluştur"""
        try:
            logger.info("Excel rapor oluşturuluyor...")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Özet sayfası
                summary_data = {
                    'Kategori': [
                        'Rapor Tarihi',
                        'Hasta Yaşı',
                        'Cinsiyet',
                        'BMI',
                        'Toplam Risk Skoru',
                        'Risk Kategorisi',
                        'Birincil Teşhis',
                        'Güven Oranı',
                        'Tespit Edilen Semptom Sayısı'
                    ],
                    'Değer': [
                        datetime.now().strftime('%d.%m.%Y %H:%M'),
                        f"{lifestyle_data.get('age', 'Belirtilmemiş')} yaş",
                        lifestyle_data.get('gender', 'Belirtilmemiş'),
                        self.calculate_bmi(lifestyle_data),
                        f"{analysis_results['risk_analysis'].get('total_score', 0):.1f}/10",
                        analysis_results['risk_analysis'].get('risk_category', 'Bilinmeyen'),
                        analysis_results['diagnosis_prediction'].get('primary_diagnosis', 'Belirsiz'),
                        f"{analysis_results['diagnosis_prediction'].get('confidence', 0):.1f}%",
                        len(analysis_results['symptom_analysis'].get('detected_symptoms', []))
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Özet', index=False)
                
                # Risk analizi sayfası
                risk_data = []
                risk_analysis = analysis_results['risk_analysis']
                
                for risk_type in ['genetic_risk', 'lifestyle_risk', 'medical_history_risk', 'family_history_risk']:
                    if risk_type in risk_analysis:
                        risk_data.append({
                            'Risk Faktörü': risk_type.replace('_', ' ').title(),
                            'Skor': risk_analysis[risk_type],
                            'Değerlendirme': self.get_risk_evaluation(risk_analysis[risk_type])
                        })
                
                risk_df = pd.DataFrame(risk_data)
                risk_df.to_excel(writer, sheet_name='Risk Analizi', index=False)
                
                # Semptom analizi sayfası
                symptom_data = []
                detected_symptoms = analysis_results['symptom_analysis'].get('detected_symptoms', [])
                
                for symptom in detected_symptoms:
                    symptom_data.append({
                        'Semptom': symptom,
                        'Durum': 'Tespit Edildi'
                    })
                
                if symptom_data:
                    symptom_df = pd.DataFrame(symptom_data)
                    symptom_df.to_excel(writer, sheet_name='Semptom Analizi', index=False)
                
                # Teşhis tahmini sayfası
                diagnosis_data = [{
                    'Teşhis Türü': 'Birincil Teşhis',
                    'Teşhis': analysis_results['diagnosis_prediction'].get('primary_diagnosis', 'Belirsiz'),
                    'Güven Oranı': f"{analysis_results['diagnosis_prediction'].get('confidence', 0):.1f}%",
                    'ICD-10 Kodu': analysis_results['diagnosis_prediction'].get('icd10_code', 'Bilinmeyen')
                }]
                
                # Ayırıcı teşhisler
                differential_diagnosis = analysis_results['diagnosis_prediction'].get('differential_diagnosis', [])
                for i, diag in enumerate(differential_diagnosis[:5], 1):
                    diagnosis_data.append({
                        'Teşhis Türü': f'Ayırıcı Teşhis {i}',
                        'Teşhis': diag.get('name', 'Bilinmeyen'),
                        'Güven Oranı': f"{diag.get('probability', 0):.1f}%",
                        'ICD-10 Kodu': ''
                    })
                
                diagnosis_df = pd.DataFrame(diagnosis_data)
                diagnosis_df.to_excel(writer, sheet_name='Teşhis Tahmini', index=False)
                
                # Öneriler sayfası
                recommendations_data = []
                recommendations = analysis_results['recommendations']
                
                for category, recs in recommendations.items():
                    if recs:
                        for rec in recs:
                            recommendations_data.append({
                                'Kategori': category.replace('_', ' ').title(),
                                'Öneri': rec
                            })
                
                if recommendations_data:
                    recommendations_df = pd.DataFrame(recommendations_data)
                    recommendations_df.to_excel(writer, sheet_name='Öneriler', index=False)
                
                # Yaşam tarzı sayfası
                lifestyle_analysis_data = [
                    {'Faktör': 'Sigara Kullanımı', 'Durum': lifestyle_data.get('smoking', 'Belirtilmemiş'), 'Değerlendirme': self.evaluate_smoking(lifestyle_data.get('smoking', ''))},
                    {'Faktör': 'Alkol Kullanımı', 'Durum': lifestyle_data.get('alcohol', 'Belirtilmemiş'), 'Değerlendirme': self.evaluate_alcohol(lifestyle_data.get('alcohol', ''))},
                    {'Faktör': 'Egzersiz Sıklığı', 'Durum': lifestyle_data.get('exercise', 'Belirtilmemiş'), 'Değerlendirme': self.evaluate_exercise(lifestyle_data.get('exercise', ''))},
                    {'Faktör': 'Günlük Uyku', 'Durum': f"{lifestyle_data.get('sleep_hours', 'Belirtilmemiş')} saat", 'Değerlendirme': self.evaluate_sleep(lifestyle_data.get('sleep_hours', 0))},
                    {'Faktör': 'Stres Seviyesi', 'Durum': f"{lifestyle_data.get('stress_level', 'Belirtilmemiş')}/10", 'Değerlendirme': self.evaluate_stress(lifestyle_data.get('stress_level', 0))}
                ]
                
                lifestyle_df = pd.DataFrame(lifestyle_analysis_data)
                lifestyle_df.to_excel(writer, sheet_name='Yaşam Tarzı', index=False)
            
            logger.info(f"Excel rapor oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Excel rapor oluşturma hatası: {str(e)}")
            return False
    
    def calculate_bmi(self, lifestyle_data):
        """BMI hesapla"""
        try:
            height = lifestyle_data.get('height')
            weight = lifestyle_data.get('weight')
            
            if height and weight:
                height_m = height / 100
                bmi = weight / (height_m ** 2)
                return f"{bmi:.1f}"
            else:
                return "Hesaplanamadı"
        except:
            return "Hesaplanamadı"