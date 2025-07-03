#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Ana Analiz Motoru
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import logging
import pickle
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """Ana sağlık analiz motoru"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.disease_database = self._load_disease_database()
        self.symptom_patterns = self._load_symptom_patterns()
        
    def _load_disease_database(self):
        """Hastalık veritabanını yükle"""
        # Basitleştirilmiş hastalık veritabanı
        diseases = {
            'diabetes': {
                'symptoms': ['yorgunluk', 'susuzluk', 'sık idrara çıkma', 'bulanık görme', 'yavaş iyileşen yaralar'],
                'risk_factors': ['obezite', 'aile geçmişi', 'yaş', 'hareketsizlik'],
                'severity': 'orta',
                'icd10': 'E11'
            },
            'hipertansiyon': {
                'symptoms': ['baş ağrısı', 'baş dönmesi', 'nefes darlığı', 'göğüs ağrısı'],
                'risk_factors': ['yaş', 'obezite', 'tuz tüketimi', 'stres', 'sigara'],
                'severity': 'orta',
                'icd10': 'I10'
            },
            'kalp_hastaligi': {
                'symptoms': ['göğüs ağrısı', 'nefes darlığı', 'yorgunluk', 'çarpıntı', 'bacak şişmesi'],
                'risk_factors': ['yaş', 'sigara', 'yüksek kolesterol', 'hipertansiyon', 'diabetes'],
                'severity': 'yüksek',
                'icd10': 'I25'
            },
            'depresyon': {
                'symptoms': ['üzüntü', 'umutsuzluk', 'enerji eksikliği', 'uyku bozukluğu', 'iştahsızlık'],
                'risk_factors': ['stres', 'aile geçmişi', 'travma', 'kronik hastalık'],
                'severity': 'orta',
                'icd10': 'F32'
            },
            'migren': {
                'symptoms': ['şiddetli baş ağrısı', 'bulantı', 'ışık hassasiyeti', 'ses hassasiyeti'],
                'risk_factors': ['stres', 'hormonal değişiklik', 'uyku bozukluğu', 'aile geçmişi'],
                'severity': 'düşük',
                'icd10': 'G43'
            },
            'anksiyete': {
                'symptoms': ['endişe', 'huzursuzluk', 'çarpıntı', 'terleme', 'nefes darlığı'],
                'risk_factors': ['stres', 'travma', 'aile geçmişi', 'kafein'],
                'severity': 'orta',
                'icd10': 'F41'
            }
        }
        return diseases
    
    def _load_symptom_patterns(self):
        """Semptom kalıplarını yükle"""
        patterns = {
            # Kardiyovasküler
            'kardiyovasküler': ['göğüs ağrısı', 'nefes darlığı', 'çarpıntı', 'baş dönmesi', 'yorgunluk'],
            
            # Metabolik
            'metabolik': ['yorgunluk', 'susuzluk', 'kilo kaybı', 'kilo alımı', 'iştah değişikliği'],
            
            # Nörolojik
            'nörolojik': ['baş ağrısı', 'baş dönmesi', 'uyuşma', 'karıncalanma', 'koordinasyon bozukluğu'],
            
            # Psikiyatrik
            'psikiyatrik': ['üzüntü', 'endişe', 'uyku bozukluğu', 'konsantrasyon sorunu', 'ruh hali değişikliği'],
            
            # Gastrointestinal
            'gastrointestinal': ['karın ağrısı', 'bulantı', 'kusma', 'ishal', 'kabızlık'],
            
            # Solunum
            'solunum': ['nefes darlığı', 'öksürük', 'göğüs ağrısı', 'hırıltı', 'balgam']
        }
        return patterns
    
    def preprocess_data(self, data_dict):
        """Veriyi ön işleme"""
        logger.info("Veri ön işleme başlatılıyor...")
        
        processed_data = {}
        
        for data_type, df in data_dict.items():
            if df is not None and not df.empty:
                # Eksik değerleri doldur
                df_processed = df.copy()
                
                # Numerik sütunlar için ortalama ile doldur
                numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
                df_processed[numeric_columns] = df_processed[numeric_columns].fillna(
                    df_processed[numeric_columns].mean()
                )
                
                # Kategorik sütunlar için mod ile doldur
                categorical_columns = df_processed.select_dtypes(include=['object', 'category']).columns
                for col in categorical_columns:
                    df_processed[col] = df_processed[col].fillna(df_processed[col].mode().iloc[0] if not df_processed[col].mode().empty else 'unknown')
                
                processed_data[data_type] = df_processed
                logger.info(f"{data_type} verisi işlendi: {df_processed.shape}")
        
        return processed_data
    
    def analyze_symptoms(self, symptoms_text):
        """Semptomları analiz et"""
        logger.info("Semptom analizi başlatılıyor...")
        
        symptoms_text = symptoms_text.lower()
        
        # Semptom eşleştirme
        detected_symptoms = []
        symptom_categories = {}
        
        # Her hastalık için semptom eşleştirmesi
        for disease, info in self.disease_database.items():
            matches = 0
            matched_symptoms = []
            
            for symptom in info['symptoms']:
                if symptom.lower() in symptoms_text:
                    matches += 1
                    matched_symptoms.append(symptom)
                    detected_symptoms.append(symptom)
            
            if matches > 0:
                symptom_categories[disease] = {
                    'matches': matches,
                    'total_symptoms': len(info['symptoms']),
                    'match_ratio': matches / len(info['symptoms']),
                    'matched_symptoms': matched_symptoms,
                    'severity': info['severity']
                }
        
        # Sistem kategorilerine göre grupla
        system_analysis = {}
        for system, system_symptoms in self.symptom_patterns.items():
            system_matches = 0
            for symptom in system_symptoms:
                if symptom.lower() in symptoms_text:
                    system_matches += 1
            
            if system_matches > 0:
                system_analysis[system] = {
                    'matches': system_matches,
                    'total': len(system_symptoms),
                    'ratio': system_matches / len(system_symptoms)
                }
        
        analysis_result = {
            'detected_symptoms': list(set(detected_symptoms)),
            'symptom_categories': symptom_categories,
            'system_analysis': system_analysis,
            'total_symptoms_detected': len(set(detected_symptoms)),
            'primary_system': max(system_analysis.keys(), key=lambda x: system_analysis[x]['ratio']) if system_analysis else None
        }
        
        logger.info(f"Semptom analizi tamamlandı: {len(detected_symptoms)} semptom tespit edildi")
        return analysis_result
    
    def calculate_risk_score(self, processed_data, lifestyle_data):
        """Risk skorunu hesapla"""
        logger.info("Risk skoru hesaplanıyor...")
        
        risk_factors = {
            'genetic_risk': 0,
            'lifestyle_risk': 0,
            'medical_history_risk': 0,
            'family_history_risk': 0
        }
        
        # Genetik risk hesaplama
        if 'genetic' in processed_data:
            genetic_df = processed_data['genetic']
            if 'risk_allele' in genetic_df.columns:
                # Risk allellerinin sayısına göre skor
                risk_alleles = genetic_df['risk_allele'].notna().sum()
                total_snps = len(genetic_df)
                risk_factors['genetic_risk'] = min((risk_alleles / total_snps) * 10, 10) if total_snps > 0 else 0
        
        # Yaşam tarzı riski
        lifestyle_risk = 0
        
        # Yaş riski
        age = lifestyle_data.get('age', 30)
        if age > 65:
            lifestyle_risk += 2
        elif age > 45:
            lifestyle_risk += 1
        
        # BMI riski
        height = lifestyle_data.get('height', 170) / 100  # cm to m
        weight = lifestyle_data.get('weight', 70)
        bmi = weight / (height ** 2)
        
        if bmi > 30:
            lifestyle_risk += 2
        elif bmi > 25:
            lifestyle_risk += 1
        
        # Sigara riski
        smoking = lifestyle_data.get('smoking', 'Hiç içmem')
        if smoking == 'Günlük':
            lifestyle_risk += 3
        elif smoking == 'Ara sıra':
            lifestyle_risk += 1
        
        # Alkol riski
        alcohol = lifestyle_data.get('alcohol', 'Hiç içmem')
        if alcohol == 'Günlük':
            lifestyle_risk += 2
        elif alcohol == 'Haftalık':
            lifestyle_risk += 1
        
        # Egzersiz riski (ters orantılı)
        exercise = lifestyle_data.get('exercise', 'Hiç')
        if exercise == 'Hiç':
            lifestyle_risk += 2
        elif exercise == '1-2 gün':
            lifestyle_risk += 1
        
        # Uyku riski
        sleep_hours = lifestyle_data.get('sleep_hours', 8)
        if sleep_hours < 6 or sleep_hours > 9:
            lifestyle_risk += 1
        
        # Stres riski
        stress_level = lifestyle_data.get('stress_level', 5)
        if stress_level > 7:
            lifestyle_risk += 2
        elif stress_level > 5:
            lifestyle_risk += 1
        
        risk_factors['lifestyle_risk'] = min(lifestyle_risk, 10)
        
        # Tıbbi geçmiş riski
        if 'medical' in processed_data:
            medical_df = processed_data['medical']
            if not medical_df.empty:
                # Kronik hastalık sayısı
                chronic_conditions = ['diabetes', 'hipertansiyon', 'kalp hastalığı', 'kanser']
                if 'diagnosis' in medical_df.columns:
                    chronic_count = 0
                    for condition in chronic_conditions:
                        if medical_df['diagnosis'].str.contains(condition, case=False, na=False).any():
                            chronic_count += 1
                    risk_factors['medical_history_risk'] = min(chronic_count * 2, 10)
        
        # Aile geçmişi riski
        if 'family' in processed_data:
            family_df = processed_data['family']
            if not family_df.empty and 'diagnosis' in family_df.columns:
                family_conditions = family_df['diagnosis'].str.lower().tolist()
                family_risk = 0
                
                high_risk_conditions = ['kalp hastalığı', 'kanser', 'diabetes', 'alzheimer']
                for condition in high_risk_conditions:
                    if any(condition in str(diag) for diag in family_conditions):
                        family_risk += 1
                
                risk_factors['family_history_risk'] = min(family_risk * 1.5, 10)
        
        # Toplam risk skoru
        total_score = np.mean(list(risk_factors.values()))
        risk_factors['total_score'] = total_score
        
        # Risk kategorisi
        if total_score < 3:
            risk_factors['risk_category'] = 'Düşük'
        elif total_score < 6:
            risk_factors['risk_category'] = 'Orta'
        else:
            risk_factors['risk_category'] = 'Yüksek'
        
        logger.info(f"Risk skoru hesaplandı: {total_score:.2f}")
        return risk_factors
    
    def predict_diagnosis(self, processed_data, symptom_analysis):
        """Teşhis tahmini yap"""
        logger.info("Teşhis tahmini başlatılıyor...")
        
        # Semptom kategorilerinden en yüksek eşleşmeyi bul
        symptom_categories = symptom_analysis.get('symptom_categories', {})
        
        if not symptom_categories:
            return {
                'primary_diagnosis': 'Belirsiz',
                'confidence': 0,
                'differential_diagnosis': [],
                'recommendation': 'Daha detaylı muayene gerekli'
            }
        
        # Hastalıkları eşleşme oranına göre sırala
        sorted_diseases = sorted(
            symptom_categories.items(),
            key=lambda x: x[1]['match_ratio'],
            reverse=True
        )
        
        primary_disease = sorted_diseases[0]
        primary_diagnosis = primary_disease[0]
        confidence = primary_disease[1]['match_ratio'] * 100
        
        # Ayırıcı teşhisler
        differential_diagnosis = []
        for disease, info in sorted_diseases[1:6]:  # İlk 5 alternatif
            differential_diagnosis.append({
                'name': disease,
                'probability': info['match_ratio'] * 100,
                'matched_symptoms': info['matched_symptoms']
            })
        
        # Güven seviyesine göre öneri
        if confidence > 70:
            recommendation = f"{primary_diagnosis} için uzman doktor kontrolü önerilir"
        elif confidence > 40:
            recommendation = f"Belirti profili {primary_diagnosis} ile uyumlu, doktor değerlendirmesi gerekli"
        else:
            recommendation = "Belirsiz semptom profili, kapsamlı tıbbi değerlendirme önerilir"
        
        result = {
            'primary_diagnosis': primary_diagnosis,
            'confidence': confidence,
            'differential_diagnosis': differential_diagnosis,
            'recommendation': recommendation,
            'icd10_code': self.disease_database.get(primary_diagnosis, {}).get('icd10', 'Unknown')
        }
        
        logger.info(f"Teşhis tahmini tamamlandı: {primary_diagnosis} (%{confidence:.1f})")
        return result
    
    def generate_recommendations(self, risk_analysis, diagnosis_prediction, lifestyle_data):
        """Kişisel öneriler oluştur"""
        logger.info("Öneriler oluşturuluyor...")
        
        recommendations = {
            'immediate_actions': [],
            'lifestyle_recommendations': [],
            'medical_recommendations': [],
            'follow_up': []
        }
        
        # Risk seviyesine göre acil öneriler
        risk_category = risk_analysis.get('risk_category', 'Düşük')
        total_risk = risk_analysis.get('total_score', 0)
        
        if risk_category == 'Yüksek' or total_risk > 7:
            recommendations['immediate_actions'].extend([
                'Acil olarak bir sağlık profesyoneline başvurun',
                'Kan basıncı ve kan şekeri kontrolü yaptırın',
                'Mevcut ilaçlarınızı gözden geçirin'
            ])
        
        # Yaşam tarzı önerileri
        lifestyle_risk = risk_analysis.get('lifestyle_risk', 0)
        
        # BMI önerileri
        height = lifestyle_data.get('height', 170) / 100
        weight = lifestyle_data.get('weight', 70)
        bmi = weight / (height ** 2)
        
        if bmi > 30:
            recommendations['lifestyle_recommendations'].append('Kilo verme programı başlatın (hedef BMI: 18.5-24.9)')
        elif bmi > 25:
            recommendations['lifestyle_recommendations'].append('Sağlıklı beslenme ve düzenli egzersiz ile ideal kiloya ulaşın')
        
        # Sigara önerileri
        smoking = lifestyle_data.get('smoking', 'Hiç içmem')
        if smoking in ['Günlük', 'Ara sıra']:
            recommendations['lifestyle_recommendations'].append('Sigara bırakma programına katılın')
            recommendations['medical_recommendations'].append('Sigara bırakma danışmanlığı alın')
        
        # Egzersiz önerileri
        exercise = lifestyle_data.get('exercise', 'Hiç')
        if exercise == 'Hiç':
            recommendations['lifestyle_recommendations'].append('Haftada en az 150 dakika orta şiddetli egzersiz yapın')
        elif exercise == '1-2 gün':
            recommendations['lifestyle_recommendations'].append('Egzersiz sıklığınızı haftada 3-4 güne çıkarın')
        
        # Uyku önerileri
        sleep_hours = lifestyle_data.get('sleep_hours', 8)
        if sleep_hours < 7:
            recommendations['lifestyle_recommendations'].append('Günlük 7-9 saat kaliteli uyku alın')
        elif sleep_hours > 9:
            recommendations['lifestyle_recommendations'].append('Uyku düzeninizi gözden geçirin, aşırı uyku da zararlı olabilir')
        
        # Stres önerileri
        stress_level = lifestyle_data.get('stress_level', 5)
        if stress_level > 6:
            recommendations['lifestyle_recommendations'].extend([
                'Stres yönetimi teknikleri öğrenin (meditasyon, nefes egzersizleri)',
                'Düzenli fiziksel aktivite ile stresi azaltın'
            ])
        
        # Teşhise özel öneriler
        primary_diagnosis = diagnosis_prediction.get('primary_diagnosis', '')
        confidence = diagnosis_prediction.get('confidence', 0)
        
        if confidence > 50:
            if 'diabetes' in primary_diagnosis.lower():
                recommendations['medical_recommendations'].extend([
                    'HbA1c ve açlık kan şekeri testi yaptırın',
                    'Diyetisyen kontrolü alın',
                    'Kan şekeri takibi yapın'
                ])
                recommendations['lifestyle_recommendations'].extend([
                    'Şekerli gıdaları sınırlayın',
                    'Düzenli öğün saatleri belirleyin',
                    'Karbonhidrat sayımı öğrenin'
                ])
            
            elif 'hipertansiyon' in primary_diagnosis.lower():
                recommendations['medical_recommendations'].extend([
                    'Düzenli kan basıncı ölçümü yapın',
                    'Kardiyoloji kontrolü yaptırın'
                ])
                recommendations['lifestyle_recommendations'].extend([
                    'Tuz tüketimini azaltın (günlük 5g altı)',
                    'DASH diyeti uygulayın',
                    'Düzenli aerobik egzersiz yapın'
                ])
            
            elif 'kalp' in primary_diagnosis.lower():
                recommendations['medical_recommendations'].extend([
                    'EKG ve ekokardiyografi yaptırın',
                    'Kardiyoloji uzmanına başvurun',
                    'Kolesterol profili kontrolü yaptırın'
                ])
                recommendations['immediate_actions'].append('Göğüs ağrısı durumunda acil servise başvurun')
            
            elif 'depresyon' in primary_diagnosis.lower():
                recommendations['medical_recommendations'].extend([
                    'Psikiyatri veya psikoloji uzmanına başvurun',
                    'Depresyon tarama testleri yaptırın'
                ])
                recommendations['lifestyle_recommendations'].extend([
                    'Sosyal aktivitelere katılın',
                    'Düzenli uyku düzeni oluşturun',
                    'Güneş ışığından yararlanın'
                ])
        
        # Takip önerileri
        if risk_category == 'Yüksek':
            recommendations['follow_up'].extend([
                '3 ay içinde kontrol muayenesi',
                'Aylık kan basıncı takibi',
                'Risk faktörlerinin düzenli değerlendirilmesi'
            ])
        elif risk_category == 'Orta':
            recommendations['follow_up'].extend([
                '6 ay içinde kontrol muayenesi',
                'Yaşam tarzı değişikliklerinin takibi'
            ])
        else:
            recommendations['follow_up'].append('Yıllık genel sağlık kontrolü')
        
        # Genel sağlık önerileri
        recommendations['lifestyle_recommendations'].extend([
            'Bol su için (günlük 2-3 litre)',
            'Sebze ve meyve tüketimini artırın',
            'İşlenmiş gıdaları sınırlayın'
        ])
        
        logger.info("Öneriler oluşturuldu")
        return recommendations
    
    def train_custom_model(self, training_data, target_column):
        """Özel model eğitimi"""
        logger.info("Özel model eğitimi başlatılıyor...")
        
        try:
            # Veriyi hazırla
            X = training_data.drop(columns=[target_column])
            y = training_data[target_column]
            
            # Kategorik verileri encode et
            for column in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X[column] = le.fit_transform(X[column].astype(str))
                self.encoders[column] = le
            
            # Veriyi ölçekle
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers['main'] = scaler
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Model eğitimi
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)
            
            # Model değerlendirmesi
            y_pred = rf_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models['random_forest'] = rf_model
            
            logger.info(f"Model eğitimi tamamlandı. Doğruluk: {accuracy:.3f}")
            
            # Modeli kaydet
            self.save_model('random_forest')
            
            return {
                'model_type': 'RandomForest',
                'accuracy': accuracy,
                'feature_importance': dict(zip(X.columns, rf_model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Model eğitimi hatası: {str(e)}")
            raise
    
    def save_model(self, model_name):
        """Modeli kaydet"""
        model_dir = Path('models')
        model_dir.mkdir(exist_ok=True)
        
        if model_name in self.models:
            with open(model_dir / f'{model_name}.pkl', 'wb') as f:
                pickle.dump(self.models[model_name], f)
            
            # Scaler ve encoder'ları da kaydet
            if self.scalers:
                with open(model_dir / 'scalers.pkl', 'wb') as f:
                    pickle.dump(self.scalers, f)
            
            if self.encoders:
                with open(model_dir / 'encoders.pkl', 'wb') as f:
                    pickle.dump(self.encoders, f)
            
            logger.info(f"Model kaydedildi: {model_name}")
    
    def load_model(self, model_name):
        """Modeli yükle"""
        model_dir = Path('models')
        model_path = model_dir / f'{model_name}.pkl'
        
        if model_path.exists():
            with open(model_path, 'rb') as f:
                self.models[model_name] = pickle.load(f)
            
            # Scaler ve encoder'ları yükle
            scaler_path = model_dir / 'scalers.pkl'
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scalers = pickle.load(f)
            
            encoder_path = model_dir / 'encoders.pkl'
            if encoder_path.exists():
                with open(encoder_path, 'rb') as f:
                    self.encoders = pickle.load(f)
            
            logger.info(f"Model yüklendi: {model_name}")
            return True
        
        return False