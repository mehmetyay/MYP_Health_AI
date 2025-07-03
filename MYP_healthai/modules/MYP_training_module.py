#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Kendi Kendini Geliştirme Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import pandas as pd
import numpy as np
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)

class TrainingModule:
    """Sistemin kendi kendini geliştirmesi için eğitim modülü"""
    
    def __init__(self):
        self.db_path = Path('data/training_data.db')
        self.feedback_data = []
        self.performance_metrics = {}
        self.learning_history = []
        self.init_database()
        
    def init_database(self):
        """Eğitim veritabanını başlat"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Kullanıcı geri bildirimleri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_symptoms TEXT NOT NULL,
                    predicted_diagnosis TEXT NOT NULL,
                    actual_diagnosis TEXT,
                    user_rating INTEGER,
                    feedback_text TEXT,
                    lifestyle_data TEXT,
                    analysis_results TEXT
                )
            ''')
            
            # Model performans tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    training_size INTEGER,
                    notes TEXT
                )
            ''')
            
            # Semptom-teşhis eşleştirme tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS symptom_diagnosis_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symptoms TEXT NOT NULL,
                    diagnosis TEXT NOT NULL,
                    confidence REAL,
                    verified BOOLEAN DEFAULT FALSE,
                    source TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Öğrenme geçmişi tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    learning_type TEXT NOT NULL,
                    data_points INTEGER,
                    improvement_score REAL,
                    description TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Eğitim veritabanı başlatıldı")
            
        except Exception as e:
            logger.error(f"Veritabanı başlatma hatası: {str(e)}")
    
    def collect_user_feedback(self, symptoms, predicted_diagnosis, analysis_results, 
                            lifestyle_data, user_rating=None, actual_diagnosis=None, 
                            feedback_text=None):
        """Kullanıcı geri bildirimini topla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO user_feedback 
                (timestamp, user_symptoms, predicted_diagnosis, actual_diagnosis, 
                 user_rating, feedback_text, lifestyle_data, analysis_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                symptoms,
                predicted_diagnosis,
                actual_diagnosis,
                user_rating,
                feedback_text,
                json.dumps(lifestyle_data),
                json.dumps(analysis_results)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info("Kullanıcı geri bildirimi kaydedildi")
            
            # Geri bildirim analizi
            self.analyze_feedback()
            
        except Exception as e:
            logger.error(f"Geri bildirim kaydetme hatası: {str(e)}")
    
    def analyze_feedback(self):
        """Geri bildirimleri analiz et"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Son 100 geri bildirimi al
            feedback_df = pd.read_sql_query('''
                SELECT * FROM user_feedback 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''', conn)
            
            if feedback_df.empty:
                conn.close()
                return
            
            # Doğruluk analizi
            correct_predictions = 0
            total_with_actual = 0
            
            for _, row in feedback_df.iterrows():
                if row['actual_diagnosis'] and row['predicted_diagnosis']:
                    total_with_actual += 1
                    if row['actual_diagnosis'].lower() in row['predicted_diagnosis'].lower():
                        correct_predictions += 1
            
            if total_with_actual > 0:
                accuracy = correct_predictions / total_with_actual
                self.performance_metrics['user_feedback_accuracy'] = accuracy
                logger.info(f"Kullanıcı geri bildirim doğruluğu: {accuracy:.3f}")
            
            # Kullanıcı memnuniyeti
            ratings = feedback_df['user_rating'].dropna()
            if not ratings.empty:
                avg_rating = ratings.mean()
                self.performance_metrics['average_user_rating'] = avg_rating
                logger.info(f"Ortalama kullanıcı puanı: {avg_rating:.2f}")
            
            # Yaygın hata kalıplarını tespit et
            self.identify_error_patterns(feedback_df)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Geri bildirim analizi hatası: {str(e)}")
    
    def identify_error_patterns(self, feedback_df):
        """Hata kalıplarını tespit et"""
        try:
            # Yanlış tahminleri analiz et
            wrong_predictions = feedback_df[
                (feedback_df['actual_diagnosis'].notna()) & 
                (feedback_df['predicted_diagnosis'].notna()) &
                (~feedback_df.apply(lambda row: row['actual_diagnosis'].lower() in row['predicted_diagnosis'].lower(), axis=1))
            ]
            
            if wrong_predictions.empty:
                return
            
            # Yaygın yanlış tahmin kalıpları
            error_patterns = {}
            
            for _, row in wrong_predictions.iterrows():
                predicted = row['predicted_diagnosis']
                actual = row['actual_diagnosis']
                
                pattern_key = f"{predicted} -> {actual}"
                if pattern_key not in error_patterns:
                    error_patterns[pattern_key] = {
                        'count': 0,
                        'symptoms': [],
                        'lifestyle_factors': []
                    }
                
                error_patterns[pattern_key]['count'] += 1
                error_patterns[pattern_key]['symptoms'].append(row['user_symptoms'])
                
                if row['lifestyle_data']:
                    try:
                        lifestyle = json.loads(row['lifestyle_data'])
                        error_patterns[pattern_key]['lifestyle_factors'].append(lifestyle)
                    except:
                        pass
            
            # En yaygın hata kalıplarını kaydet
            sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1]['count'], reverse=True)
            
            for pattern, data in sorted_patterns[:5]:  # İlk 5 kalıp
                logger.warning(f"Yaygın hata kalıbı: {pattern} ({data['count']} kez)")
                
                # Bu kalıp için iyileştirme önerisi oluştur
                self.create_improvement_suggestion(pattern, data)
                
        except Exception as e:
            logger.error(f"Hata kalıbı analizi hatası: {str(e)}")
    
    def create_improvement_suggestion(self, pattern, error_data):
        """İyileştirme önerisi oluştur"""
        try:
            # Semptom kalıplarını analiz et
            all_symptoms = ' '.join(error_data['symptoms']).lower()
            
            # Yaygın semptomları bul
            symptom_words = all_symptoms.split()
            symptom_freq = {}
            
            for word in symptom_words:
                if len(word) > 3:  # Kısa kelimeleri filtrele
                    symptom_freq[word] = symptom_freq.get(word, 0) + 1
            
            # En yaygın semptomlar
            common_symptoms = sorted(symptom_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            suggestion = {
                'pattern': pattern,
                'frequency': error_data['count'],
                'common_symptoms': common_symptoms,
                'improvement_actions': [
                    f"'{pattern.split(' -> ')[0]}' teşhisi için semptom ağırlıklarını gözden geçir",
                    f"'{pattern.split(' -> ')[1]}' teşhisi için yeni semptom kalıpları ekle",
                    "Ayırıcı teşhis kriterlerini güçlendir"
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            # İyileştirme önerisini kaydet
            self.save_improvement_suggestion(suggestion)
            
        except Exception as e:
            logger.error(f"İyileştirme önerisi oluşturma hatası: {str(e)}")
    
    def save_improvement_suggestion(self, suggestion):
        """İyileştirme önerisini kaydet"""
        try:
            suggestions_file = Path('data/improvement_suggestions.json')
            
            if suggestions_file.exists():
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    suggestions = json.load(f)
            else:
                suggestions = []
            
            suggestions.append(suggestion)
            
            # Son 50 öneriyi tut
            suggestions = suggestions[-50:]
            
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                json.dump(suggestions, f, ensure_ascii=False, indent=2)
            
            logger.info("İyileştirme önerisi kaydedildi")
            
        except Exception as e:
            logger.error(f"İyileştirme önerisi kaydetme hatası: {str(e)}")
    
    def update_symptom_diagnosis_mapping(self, symptoms, diagnosis, confidence, verified=False, source='user'):
        """Semptom-teşhis eşleştirmesini güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO symptom_diagnosis_mapping 
                (symptoms, diagnosis, confidence, verified, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symptoms, diagnosis, confidence, verified, source, timestamp))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Semptom-teşhis eşleştirmesi güncellendi: {diagnosis}")
            
        except Exception as e:
            logger.error(f"Eşleştirme güncelleme hatası: {str(e)}")
    
    def retrain_models(self, analysis_engine):
        """Modelleri yeniden eğit"""
        try:
            logger.info("Model yeniden eğitimi başlatılıyor...")
            
            # Eğitim verilerini topla
            training_data = self.prepare_training_data()
            
            if training_data.empty:
                logger.warning("Yeterli eğitim verisi yok")
                return False
            
            # Model performansını değerlendir
            old_performance = self.performance_metrics.copy()
            
            # Yeni model eğit
            if 'diagnosis' in training_data.columns:
                result = analysis_engine.train_custom_model(training_data, 'diagnosis')
                
                # Performans karşılaştırması
                new_accuracy = result.get('accuracy', 0)
                old_accuracy = old_performance.get('model_accuracy', 0)
                
                improvement = new_accuracy - old_accuracy
                
                # Performansı kaydet
                self.save_model_performance(
                    model_type='retrained_model',
                    accuracy=new_accuracy,
                    training_size=len(training_data),
                    notes=f"İyileşme: {improvement:.3f}"
                )
                
                # Öğrenme geçmişini kaydet
                self.record_learning_event(
                    learning_type='model_retraining',
                    data_points=len(training_data),
                    improvement_score=improvement,
                    description=f"Model yeniden eğitildi. Doğruluk: {new_accuracy:.3f}"
                )
                
                logger.info(f"Model yeniden eğitimi tamamlandı. İyileşme: {improvement:.3f}")
                return True
            
        except Exception as e:
            logger.error(f"Model yeniden eğitimi hatası: {str(e)}")
            return False
    
    def prepare_training_data(self):
        """Eğitim verilerini hazırla"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Doğrulanmış veri setini al
            query = '''
                SELECT 
                    user_symptoms as symptoms,
                    actual_diagnosis as diagnosis,
                    lifestyle_data,
                    user_rating
                FROM user_feedback 
                WHERE actual_diagnosis IS NOT NULL 
                AND user_rating >= 3
                ORDER BY timestamp DESC
                LIMIT 1000
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return pd.DataFrame()
            
            # Veriyi işle
            processed_data = []
            
            for _, row in df.iterrows():
                try:
                    # Yaşam tarzı verilerini parse et
                    lifestyle = json.loads(row['lifestyle_data']) if row['lifestyle_data'] else {}
                    
                    # Özellik vektörü oluştur
                    features = {
                        'symptoms': row['symptoms'],
                        'diagnosis': row['diagnosis'],
                        'age': lifestyle.get('age', 30),
                        'gender': lifestyle.get('gender', 'Erkek'),
                        'smoking': lifestyle.get('smoking', 'Hiç içmem'),
                        'exercise': lifestyle.get('exercise', 'Hiç'),
                        'stress_level': lifestyle.get('stress_level', 5),
                        'user_rating': row['user_rating']
                    }
                    
                    processed_data.append(features)
                    
                except Exception as e:
                    logger.warning(f"Veri işleme hatası: {str(e)}")
                    continue
            
            training_df = pd.DataFrame(processed_data)
            logger.info(f"Eğitim verisi hazırlandı: {len(training_df)} kayıt")
            
            return training_df
            
        except Exception as e:
            logger.error(f"Eğitim verisi hazırlama hatası: {str(e)}")
            return pd.DataFrame()
    
    def save_model_performance(self, model_type, accuracy, precision_score=None, 
                             recall_score=None, f1_score=None, training_size=None, notes=None):
        """Model performansını kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO model_performance 
                (timestamp, model_type, accuracy, precision_score, recall_score, 
                 f1_score, training_size, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, model_type, accuracy, precision_score, 
                recall_score, f1_score, training_size, notes
            ))
            
            conn.commit()
            conn.close()
            
            # Performans metriklerini güncelle
            self.performance_metrics.update({
                'model_accuracy': accuracy,
                'last_training_size': training_size,
                'last_update': timestamp
            })
            
            logger.info(f"Model performansı kaydedildi: {model_type}")
            
        except Exception as e:
            logger.error(f"Performans kaydetme hatası: {str(e)}")
    
    def record_learning_event(self, learning_type, data_points, improvement_score, description):
        """Öğrenme olayını kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO learning_history 
                (timestamp, learning_type, data_points, improvement_score, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, learning_type, data_points, improvement_score, description))
            
            conn.commit()
            conn.close()
            
            # Öğrenme geçmişini güncelle
            self.learning_history.append({
                'timestamp': timestamp,
                'type': learning_type,
                'data_points': data_points,
                'improvement': improvement_score,
                'description': description
            })
            
            logger.info(f"Öğrenme olayı kaydedildi: {learning_type}")
            
        except Exception as e:
            logger.error(f"Öğrenme olayı kaydetme hatası: {str(e)}")
    
    def get_learning_statistics(self):
        """Öğrenme istatistiklerini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            stats = {}
            
            # Toplam geri bildirim sayısı
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM user_feedback')
            stats['total_feedback'] = cursor.fetchone()[0]
            
            # Doğrulanmış veri sayısı
            cursor.execute('SELECT COUNT(*) FROM user_feedback WHERE actual_diagnosis IS NOT NULL')
            stats['verified_data'] = cursor.fetchone()[0]
            
            # Ortalama kullanıcı puanı
            cursor.execute('SELECT AVG(user_rating) FROM user_feedback WHERE user_rating IS NOT NULL')
            result = cursor.fetchone()[0]
            stats['average_rating'] = result if result else 0
            
            # Son model performansı
            cursor.execute('''
                SELECT accuracy, training_size, timestamp 
                FROM model_performance 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                stats['last_model_accuracy'] = result[0]
                stats['last_training_size'] = result[1]
                stats['last_training_date'] = result[2]
            
            # Öğrenme olayları sayısı
            cursor.execute('SELECT COUNT(*) FROM learning_history')
            stats['learning_events'] = cursor.fetchone()[0]
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"İstatistik alma hatası: {str(e)}")
            return {}
    
    def auto_improvement_check(self, analysis_engine):
        """Otomatik iyileştirme kontrolü"""
        try:
            stats = self.get_learning_statistics()
            
            # Yeterli veri var mı kontrol et
            min_data_threshold = 50
            if stats.get('verified_data', 0) < min_data_threshold:
                logger.info(f"Otomatik iyileştirme için yeterli veri yok ({stats.get('verified_data', 0)}/{min_data_threshold})")
                return False
            
            # Kullanıcı memnuniyeti düşük mü
            avg_rating = stats.get('average_rating', 5)
            if avg_rating < 3.5:
                logger.info("Kullanıcı memnuniyeti düşük, model iyileştirmesi gerekli")
                return self.retrain_models(analysis_engine)
            
            # Belirli aralıklarla otomatik yeniden eğitim
            last_training = stats.get('last_training_date')
            if last_training:
                from datetime import datetime, timedelta
                last_date = datetime.fromisoformat(last_training)
                if datetime.now() - last_date > timedelta(days=30):  # 30 günde bir
                    logger.info("Otomatik periyodik model güncellemesi")
                    return self.retrain_models(analysis_engine)
            
            return False
            
        except Exception as e:
            logger.error(f"Otomatik iyileştirme kontrolü hatası: {str(e)}")
            return False
    
    def export_learning_data(self, output_path):
        """Öğrenme verilerini dışa aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Tüm tabloları Excel'e aktar
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Kullanıcı geri bildirimleri
                feedback_df = pd.read_sql_query('SELECT * FROM user_feedback', conn)
                feedback_df.to_excel(writer, sheet_name='User_Feedback', index=False)
                
                # Model performansı
                performance_df = pd.read_sql_query('SELECT * FROM model_performance', conn)
                performance_df.to_excel(writer, sheet_name='Model_Performance', index=False)
                
                # Semptom-teşhis eşleştirmeleri
                mapping_df = pd.read_sql_query('SELECT * FROM symptom_diagnosis_mapping', conn)
                mapping_df.to_excel(writer, sheet_name='Symptom_Diagnosis', index=False)
                
                # Öğrenme geçmişi
                history_df = pd.read_sql_query('SELECT * FROM learning_history', conn)
                history_df.to_excel(writer, sheet_name='Learning_History', index=False)
            
            conn.close()
            logger.info(f"Öğrenme verileri dışa aktarıldı: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Veri dışa aktarma hatası: {str(e)}")
            return False