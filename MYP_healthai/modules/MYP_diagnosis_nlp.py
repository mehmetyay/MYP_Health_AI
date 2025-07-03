#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Doğal Dil İşleme ve Teşhis Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import re
import json
from pathlib import Path
import logging
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

class DiagnosisNLP:
    """Semptom analizi ve teşhis için NLP modülü"""
    
    def __init__(self):
        self.symptom_dictionary = self._load_symptom_dictionary()
        self.medical_terms = self._load_medical_terms()
        self.severity_indicators = self._load_severity_indicators()
        self.negation_words = ['değil', 'yok', 'hiç', 'asla', 'olmayan', 'bulunmayan']
        
    def _load_symptom_dictionary(self):
        """Semptom sözlüğünü yükle"""
        symptoms = {
            # Genel semptomlar
            'ateş': ['ateş', 'yüksek ateş', 'humma', 'sıcaklık'],
            'yorgunluk': ['yorgunluk', 'bitkinlik', 'halsizlik', 'güçsüzlük', 'enerji eksikliği'],
            'baş_ağrısı': ['baş ağrısı', 'başım ağrıyor', 'migren', 'baş zonklaması'],
            'baş_dönmesi': ['baş dönmesi', 'sersemlik', 'dengesizlik', 'vertigo'],
            
            # Kardiyovasküler
            'göğüs_ağrısı': ['göğüs ağrısı', 'göğsümde ağrı', 'kalp ağrısı', 'angina'],
            'nefes_darlığı': ['nefes darlığı', 'nefes alamıyorum', 'dispne', 'soluk darlığı'],
            'çarpıntı': ['çarpıntı', 'kalp çarpıntısı', 'taşikardi', 'kalp hızlı atıyor'],
            
            # Gastrointestinal
            'karın_ağrısı': ['karın ağrısı', 'mide ağrısı', 'karın krampları', 'abdominal ağrı'],
            'bulantı': ['bulantı', 'mide bulantısı', 'kusma hissi'],
            'kusma': ['kusma', 'kusmak', 'istifra'],
            'ishal': ['ishal', 'diyare', 'sulu dışkı'],
            'kabızlık': ['kabızlık', 'konstipasyon', 'dışkı yapamama'],
            
            # Nörolojik
            'uyuşma': ['uyuşma', 'his kaybı', 'parestezi', 'karıncalanma'],
            'titreme': ['titreme', 'tremor', 'sarsıntı'],
            'konvülsiyon': ['konvülsiyon', 'nöbet', 'kasılma', 'epilepsi'],
            
            # Psikiyatrik
            'depresyon': ['depresyon', 'üzüntü', 'mutsuzluk', 'çökkünlük', 'melankolik'],
            'anksiyete': ['anksiyete', 'endişe', 'kaygı', 'gerginlik', 'stres'],
            'uykusuzluk': ['uykusuzluk', 'insomnia', 'uyuyamama', 'uyku bozukluğu'],
            
            # Solunum sistemi
            'öksürük': ['öksürük', 'öksürme', 'kuru öksürük', 'balgamlı öksürük'],
            'balgam': ['balgam', 'köpük', 'ekspektorasyon'],
            'hırıltı': ['hırıltı', 'wheezing', 'ıslık sesi'],
            
            # Kas-iskelet sistemi
            'kas_ağrısı': ['kas ağrısı', 'miyalji', 'kas krampları', 'kas gerginliği'],
            'eklem_ağrısı': ['eklem ağrısı', 'artralji', 'romatizma', 'artrit'],
            'sırt_ağrısı': ['sırt ağrısı', 'bel ağrısı', 'lombalji'],
            
            # Deri
            'kaşıntı': ['kaşıntı', 'kaşınma', 'pruritus'],
            'döküntü': ['döküntü', 'kızarıklık', 'rash', 'egzama'],
            'şişlik': ['şişlik', 'ödem', 'şişme', 'büyüme'],
            
            # Göz-kulak-burun-boğaz
            'görme_bozukluğu': ['görme bozukluğu', 'bulanık görme', 'çift görme'],
            'işitme_kaybı': ['işitme kaybı', 'sağırlık', 'kulak tıkanıklığı'],
            'boğaz_ağrısı': ['boğaz ağrısı', 'yutma güçlüğü', 'farenjit'],
            'burun_akıntısı': ['burun akıntısı', 'rinit', 'nezle'],
            
            # Ürogenital
            'idrar_yakınması': ['idrar yakınması', 'dizüri', 'yanma', 'sistit'],
            'sık_idrara_çıkma': ['sık idrara çıkma', 'poliüri', 'sık tuvalete gitme'],
            
            # Metabolik
            'susuzluk': ['susuzluk', 'ağız kuruluğu', 'polidipsi'],
            'iştah_kaybı': ['iştah kaybı', 'anoreksiya', 'yemek istememe'],
            'kilo_kaybı': ['kilo kaybı', 'zayıflama', 'kilo verme'],
            'kilo_alımı': ['kilo alımı', 'şişmanlama', 'kilo artışı']
        }
        return symptoms
    
    def _load_medical_terms(self):
        """Tıbbi terimler sözlüğü"""
        terms = {
            'anatomical_regions': [
                'baş', 'boyun', 'göğüs', 'karın', 'sırt', 'bel', 'kol', 'bacak',
                'kalp', 'akciğer', 'mide', 'karaciğer', 'böbrek', 'beyin'
            ],
            'time_indicators': [
                'sabah', 'akşam', 'gece', 'sürekli', 'ara sıra', 'bazen',
                'her zaman', 'son zamanlarda', 'uzun süredir', 'kısa süre'
            ],
            'intensity_modifiers': [
                'çok', 'az', 'biraz', 'oldukça', 'son derece', 'hafif',
                'orta', 'şiddetli', 'dayanılmaz', 'katlanılmaz'
            ]
        }
        return terms
    
    def _load_severity_indicators(self):
        """Şiddet göstergeleri"""
        severity = {
            'mild': ['hafif', 'az', 'biraz', 'ufak', 'küçük'],
            'moderate': ['orta', 'normal', 'standart', 'tipik'],
            'severe': ['şiddetli', 'çok', 'aşırı', 'dayanılmaz', 'korkunç', 'berbat']
        }
        return severity
    
    def extract_symptoms(self, text):
        """Metinden semptomları çıkar"""
        logger.info("Semptom çıkarımı başlatılıyor...")
        
        text = text.lower().strip()
        extracted_symptoms = {}
        
        # Her semptom kategorisi için kontrol et
        for symptom_key, symptom_variants in self.symptom_dictionary.items():
            for variant in symptom_variants:
                if variant in text:
                    # Negasyon kontrolü
                    if not self._is_negated(text, variant):
                        severity = self._extract_severity(text, variant)
                        timing = self._extract_timing(text, variant)
                        location = self._extract_location(text, variant)
                        
                        extracted_symptoms[symptom_key] = {
                            'found_variant': variant,
                            'severity': severity,
                            'timing': timing,
                            'location': location,
                            'confidence': self._calculate_confidence(text, variant)
                        }
                        break  # İlk eşleşmeyi al
        
        logger.info(f"{len(extracted_symptoms)} semptom çıkarıldı")
        return extracted_symptoms
    
    def _is_negated(self, text, symptom):
        """Semptomu olumsuzlayan ifade var mı kontrol et"""
        # Semptomu içeren cümleyi bul
        sentences = re.split(r'[.!?]', text)
        symptom_sentence = None
        
        for sentence in sentences:
            if symptom in sentence:
                symptom_sentence = sentence
                break
        
        if not symptom_sentence:
            return False
        
        # Olumsuzlama kelimelerini kontrol et
        for negation in self.negation_words:
            if negation in symptom_sentence:
                # Olumsuzlama kelimesi semptomu önce mi geliyor
                neg_pos = symptom_sentence.find(negation)
                symp_pos = symptom_sentence.find(symptom)
                if neg_pos < symp_pos and symp_pos - neg_pos < 50:  # 50 karakter yakınlık
                    return True
        
        return False
    
    def _extract_severity(self, text, symptom):
        """Semptom şiddetini çıkar"""
        # Semptomu içeren cümleyi bul
        sentences = re.split(r'[.!?]', text)
        symptom_sentence = None
        
        for sentence in sentences:
            if symptom in sentence:
                symptom_sentence = sentence
                break
        
        if not symptom_sentence:
            return 'unknown'
        
        # Şiddet göstergelerini kontrol et
        for severity_level, indicators in self.severity_indicators.items():
            for indicator in indicators:
                if indicator in symptom_sentence:
                    return severity_level
        
        return 'moderate'  # Varsayılan
    
    def _extract_timing(self, text, symptom):
        """Semptom zamanlamasını çıkar"""
        time_patterns = {
            'morning': ['sabah', 'sabahları', 'sabahleyin'],
            'evening': ['akşam', 'akşamları', 'akşamleyin'],
            'night': ['gece', 'geceleri', 'gece vakti'],
            'continuous': ['sürekli', 'her zaman', 'devamlı', 'hiç geçmiyor'],
            'intermittent': ['ara sıra', 'bazen', 'zaman zaman', 'arada bir'],
            'recent': ['son zamanlarda', 'yakın zamanda', 'geçenlerde'],
            'chronic': ['uzun süredir', 'aylar', 'yıllar', 'kronik']
        }
        
        sentences = re.split(r'[.!?]', text)
        symptom_sentence = None
        
        for sentence in sentences:
            if symptom in sentence:
                symptom_sentence = sentence
                break
        
        if not symptom_sentence:
            return 'unknown'
        
        for timing, patterns in time_patterns.items():
            for pattern in patterns:
                if pattern in symptom_sentence:
                    return timing
        
        return 'unknown'
    
    def _extract_location(self, text, symptom):
        """Semptom lokasyonunu çıkar"""
        anatomical_regions = self.medical_terms['anatomical_regions']
        
        sentences = re.split(r'[.!?]', text)
        symptom_sentence = None
        
        for sentence in sentences:
            if symptom in sentence:
                symptom_sentence = sentence
                break
        
        if not symptom_sentence:
            return 'unknown'
        
        for region in anatomical_regions:
            if region in symptom_sentence:
                return region
        
        return 'unknown'
    
    def _calculate_confidence(self, text, symptom):
        """Semptom güven skorunu hesapla"""
        base_confidence = 0.7
        
        # Semptomu destekleyen faktörler
        supporting_factors = 0
        
        # Şiddet belirteci varsa
        if any(indicator in text for severity_indicators in self.severity_indicators.values() 
               for indicator in severity_indicators):
            supporting_factors += 0.1
        
        # Zaman belirteci varsa
        time_indicators = ['sabah', 'akşam', 'gece', 'sürekli', 'ara sıra']
        if any(indicator in text for indicator in time_indicators):
            supporting_factors += 0.1
        
        # Lokasyon belirteci varsa
        if any(region in text for region in self.medical_terms['anatomical_regions']):
            supporting_factors += 0.1
        
        # Semptom kelimesinin tekrar sayısı
        symptom_count = text.count(symptom)
        if symptom_count > 1:
            supporting_factors += min(symptom_count * 0.05, 0.1)
        
        return min(base_confidence + supporting_factors, 1.0)
    
    def analyze_symptom_patterns(self, extracted_symptoms):
        """Semptom kalıplarını analiz et"""
        logger.info("Semptom kalıpları analiz ediliyor...")
        
        if not extracted_symptoms:
            return {}
        
        # Sistem kategorilerine göre grupla
        system_categories = {
            'cardiovascular': ['göğüs_ağrısı', 'nefes_darlığı', 'çarpıntı', 'şişlik'],
            'respiratory': ['öksürük', 'balgam', 'hırıltı', 'nefes_darlığı'],
            'gastrointestinal': ['karın_ağrısı', 'bulantı', 'kusma', 'ishal', 'kabızlık'],
            'neurological': ['baş_ağrısı', 'baş_dönmesi', 'uyuşma', 'titreme'],
            'psychiatric': ['depresyon', 'anksiyete', 'uykusuzluk'],
            'musculoskeletal': ['kas_ağrısı', 'eklem_ağrısı', 'sırt_ağrısı'],
            'dermatological': ['kaşıntı', 'döküntü', 'şişlik'],
            'metabolic': ['yorgunluk', 'susuzluk', 'iştah_kaybı', 'kilo_kaybı', 'kilo_alımı']
        }
        
        system_analysis = {}
        for system, symptoms in system_categories.items():
            system_symptoms = []
            total_confidence = 0
            
            for symptom in symptoms:
                if symptom in extracted_symptoms:
                    system_symptoms.append({
                        'symptom': symptom,
                        'details': extracted_symptoms[symptom]
                    })
                    total_confidence += extracted_symptoms[symptom]['confidence']
            
            if system_symptoms:
                system_analysis[system] = {
                    'symptoms': system_symptoms,
                    'symptom_count': len(system_symptoms),
                    'average_confidence': total_confidence / len(system_symptoms),
                    'severity_distribution': self._analyze_severity_distribution(system_symptoms)
                }
        
        return system_analysis
    
    def _analyze_severity_distribution(self, symptoms):
        """Şiddet dağılımını analiz et"""
        severities = [symptom['details']['severity'] for symptom in symptoms]
        severity_counts = Counter(severities)
        
        total = len(severities)
        distribution = {}
        for severity, count in severity_counts.items():
            distribution[severity] = {
                'count': count,
                'percentage': (count / total) * 100
            }
        
        return distribution
    
    def generate_symptom_summary(self, extracted_symptoms, system_analysis):
        """Semptom özetini oluştur"""
        summary = {
            'total_symptoms': len(extracted_symptoms),
            'primary_systems': [],
            'severity_overview': {},
            'temporal_patterns': {},
            'key_findings': []
        }
        
        # Birincil sistemleri belirle
        if system_analysis:
            sorted_systems = sorted(
                system_analysis.items(),
                key=lambda x: (x[1]['symptom_count'], x[1]['average_confidence']),
                reverse=True
            )
            
            summary['primary_systems'] = [
                {
                    'system': system,
                    'symptom_count': data['symptom_count'],
                    'confidence': data['average_confidence']
                }
                for system, data in sorted_systems[:3]
            ]
        
        # Genel şiddet dağılımı
        all_severities = [details['severity'] for details in extracted_symptoms.values()]
        severity_counts = Counter(all_severities)
        total_symptoms = len(all_severities)
        
        for severity, count in severity_counts.items():
            summary['severity_overview'][severity] = {
                'count': count,
                'percentage': (count / total_symptoms) * 100
            }
        
        # Zamansal kalıplar
        all_timings = [details['timing'] for details in extracted_symptoms.values()]
        timing_counts = Counter(all_timings)
        
        for timing, count in timing_counts.items():
            summary['temporal_patterns'][timing] = {
                'count': count,
                'percentage': (count / total_symptoms) * 100
            }
        
        # Önemli bulgular
        if severity_counts.get('severe', 0) > 0:
            summary['key_findings'].append(f"Şiddetli semptomlar tespit edildi ({severity_counts['severe']} adet)")
        
        if timing_counts.get('continuous', 0) > 0:
            summary['key_findings'].append("Sürekli semptomlar mevcut")
        
        if len(system_analysis) > 2:
            summary['key_findings'].append("Çoklu sistem tutulumu")
        
        return summary
    
    def suggest_medical_specialties(self, system_analysis):
        """Tıbbi uzmanlık önerileri"""
        specialty_mapping = {
            'cardiovascular': ['Kardiyoloji', 'İç Hastalıkları'],
            'respiratory': ['Göğüs Hastalıkları', 'İç Hastalıkları'],
            'gastrointestinal': ['Gastroenteroloji', 'İç Hastalıkları'],
            'neurological': ['Nöroloji', 'İç Hastalıkları'],
            'psychiatric': ['Psikiyatri', 'Psikoloji'],
            'musculoskeletal': ['Ortopedi', 'Fizik Tedavi', 'Romatologi'],
            'dermatological': ['Dermatoloji'],
            'metabolic': ['Endokrinoloji', 'İç Hastalıkları']
        }
        
        suggested_specialties = set()
        
        for system, data in system_analysis.items():
            if data['symptom_count'] > 0:
                specialties = specialty_mapping.get(system, ['İç Hastalıkları'])
                suggested_specialties.update(specialties)
        
        # Öncelik sıralaması
        priority_order = [
            'Acil Tıp',  # Şiddetli semptomlar varsa
            'İç Hastalıkları',  # Genel
            'Kardiyoloji',
            'Nöroloji',
            'Gastroenteroloji',
            'Göğüs Hastalıkları',
            'Psikiyatri',
            'Endokrinoloji',
            'Ortopedi',
            'Dermatoloji',
            'Romatologi',
            'Fizik Tedavi',
            'Psikoloji'
        ]
        
        # Acil durum kontrolü
        emergency_symptoms = ['göğüs_ağrısı', 'nefes_darlığı', 'konvülsiyon']
        has_emergency = any(symptom in system_analysis.get('cardiovascular', {}).get('symptoms', []) or
                           symptom in system_analysis.get('neurological', {}).get('symptoms', [])
                           for symptom in emergency_symptoms)
        
        if has_emergency:
            suggested_specialties.add('Acil Tıp')
        
        # Öncelik sırasına göre sırala
        sorted_specialties = []
        for specialty in priority_order:
            if specialty in suggested_specialties:
                sorted_specialties.append(specialty)
        
        return sorted_specialties[:5]  # İlk 5 öneri