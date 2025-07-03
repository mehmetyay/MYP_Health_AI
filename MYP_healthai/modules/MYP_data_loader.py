#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık AI - Veri Yükleme Modülü
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Çeşitli formatlardaki veri dosyalarını yükleyen sınıf"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.json', '.xml']
        
    def load_file(self, file_path, data_type):
        """
        Dosyayı formatına göre yükle
        
        Args:
            file_path (str): Dosya yolu
            data_type (str): Veri tipi (genetic, medical, family)
            
        Returns:
            pandas.DataFrame: Yüklenen veri
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_extension}")
        
        logger.info(f"Dosya yükleniyor: {file_path} (Tip: {data_type})")
        
        try:
            if file_extension == '.csv':
                return self._load_csv(file_path, data_type)
            elif file_extension == '.xlsx':
                return self._load_excel(file_path, data_type)
            elif file_extension == '.json':
                return self._load_json(file_path, data_type)
            elif file_extension == '.xml':
                return self._load_xml(file_path, data_type)
        except Exception as e:
            logger.error(f"Dosya yükleme hatası: {str(e)}")
            raise
    
    def _load_csv(self, file_path, data_type):
        """CSV dosyası yükle"""
        try:
            # Farklı encoding'leri dene
            encodings = ['utf-8', 'latin-1', 'cp1254', 'iso-8859-9']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"CSV başarıyla yüklendi ({encoding}): {df.shape}")
                    return self._validate_and_process_data(df, data_type)
                except UnicodeDecodeError:
                    continue
            
            # Hiçbir encoding çalışmazsa
            raise ValueError("Dosya encoding'i desteklenmiyor")
            
        except Exception as e:
            raise ValueError(f"CSV yükleme hatası: {str(e)}")
    
    def _load_excel(self, file_path, data_type):
        """Excel dosyası yükle"""
        try:
            # İlk sheet'i yükle
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"Excel başarıyla yüklendi: {df.shape}")
            return self._validate_and_process_data(df, data_type)
        except Exception as e:
            raise ValueError(f"Excel yükleme hatası: {str(e)}")
    
    def _load_json(self, file_path, data_type):
        """JSON dosyası yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSON'u DataFrame'e çevir
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Nested dict ise normalize et
                df = pd.json_normalize(data)
            else:
                raise ValueError("JSON formatı desteklenmiyor")
            
            logger.info(f"JSON başarıyla yüklendi: {df.shape}")
            return self._validate_and_process_data(df, data_type)
            
        except Exception as e:
            raise ValueError(f"JSON yükleme hatası: {str(e)}")
    
    def _load_xml(self, file_path, data_type):
        """XML dosyası yükle"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # XML'i dict listesine çevir
            data = []
            for child in root:
                record = {}
                for subchild in child:
                    record[subchild.tag] = subchild.text
                data.append(record)
            
            df = pd.DataFrame(data)
            logger.info(f"XML başarıyla yüklendi: {df.shape}")
            return self._validate_and_process_data(df, data_type)
            
        except Exception as e:
            raise ValueError(f"XML yükleme hatası: {str(e)}")
    
    def _validate_and_process_data(self, df, data_type):
        """Veriyi doğrula ve işle"""
        if df.empty:
            raise ValueError("Dosya boş veya veri içermiyor")
        
        # Veri tipine göre özel işlemler
        if data_type == 'genetic':
            return self._process_genetic_data(df)
        elif data_type == 'medical':
            return self._process_medical_data(df)
        elif data_type == 'family':
            return self._process_family_data(df)
        else:
            return self._process_general_data(df)
    
    def _process_genetic_data(self, df):
        """Genetik veriyi işle"""
        logger.info("Genetik veri işleniyor...")
        
        # Genetik veri için beklenen sütunlar
        expected_columns = ['snp_id', 'chromosome', 'position', 'genotype', 'risk_allele']
        
        # Sütun adlarını normalize et
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Eksik sütunları kontrol et
        missing_columns = []
        for col in expected_columns:
            if col not in df.columns:
                # Alternatif isimleri kontrol et
                alternatives = {
                    'snp_id': ['snp', 'rs_id', 'marker_id', 'id'],
                    'chromosome': ['chr', 'chrom', 'chromosome_number'],
                    'position': ['pos', 'bp_position', 'base_position'],
                    'genotype': ['gt', 'alleles', 'variant'],
                    'risk_allele': ['risk', 'risk_variant', 'pathogenic']
                }
                
                found = False
                if col in alternatives:
                    for alt in alternatives[col]:
                        if alt in df.columns:
                            df.rename(columns={alt: col}, inplace=True)
                            found = True
                            break
                
                if not found:
                    missing_columns.append(col)
        
        # Kritik sütunlar eksikse uyar
        if missing_columns:
            logger.warning(f"Genetik veri için eksik sütunlar: {missing_columns}")
        
        # Veri tiplerini düzelt
        if 'chromosome' in df.columns:
            df['chromosome'] = df['chromosome'].astype(str)
        if 'position' in df.columns:
            df['position'] = pd.to_numeric(df['position'], errors='coerce')
        
        return df
    
    def _process_medical_data(self, df):
        """Tıbbi veriyi işle"""
        logger.info("Tıbbi veri işleniyor...")
        
        # Sütun adlarını normalize et
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Tarih sütunlarını işle
        date_columns = ['date', 'diagnosis_date', 'treatment_date', 'visit_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Kategorik verileri işle
        categorical_columns = ['diagnosis', 'treatment', 'medication', 'status']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        return df
    
    def _process_family_data(self, df):
        """Aile geçmişi verisini işle"""
        logger.info("Aile geçmişi verisi işleniyor...")
        
        # Sütun adlarını normalize et
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Aile üyesi ilişkilerini standardize et
        if 'relationship' in df.columns:
            relationship_mapping = {
                'mother': 'anne',
                'father': 'baba',
                'sister': 'kız_kardeş',
                'brother': 'erkek_kardeş',
                'grandmother': 'büyükanne',
                'grandfather': 'büyükbaba'
            }
            df['relationship'] = df['relationship'].str.lower().replace(relationship_mapping)
        
        return df
    
    def _process_general_data(self, df):
        """Genel veri işleme"""
        logger.info("Genel veri işleniyor...")
        
        # Sütun adlarını normalize et
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Boş değerleri temizle
        df = df.dropna(how='all')  # Tamamen boş satırları kaldır
        
        return df
    
    def create_sample_data(self):
        """Örnek veri dosyalarını oluştur"""
        logger.info("Örnek veri dosyaları oluşturuluyor...")
        
        # Örnek genetik veri
        genetic_data = {
            'snp_id': ['rs1234567', 'rs2345678', 'rs3456789', 'rs4567890'],
            'chromosome': ['1', '2', '3', '4'],
            'position': [12345, 23456, 34567, 45678],
            'genotype': ['AA', 'AG', 'GG', 'AT'],
            'risk_allele': ['A', 'G', 'G', 'T'],
            'disease_association': ['Diabetes', 'Heart Disease', 'Cancer', 'Alzheimer']
        }
        
        genetic_df = pd.DataFrame(genetic_data)
        genetic_df.to_csv('data/sample_genetic_data.csv', index=False, encoding='utf-8')
        
        # Örnek tıbbi geçmiş
        medical_data = {
            'date': ['2023-01-15', '2023-03-20', '2023-06-10', '2023-09-05'],
            'diagnosis': ['Hipertansiyon', 'Diabetes Tip 2', 'Yüksek Kolesterol', 'Migren'],
            'treatment': ['ACE inhibitör', 'Metformin', 'Statin', 'Analjezik'],
            'status': ['Aktif', 'Kontrol altında', 'İyileşti', 'Kronik'],
            'doctor': ['Dr. Ahmet', 'Dr. Ayşe', 'Dr. Mehmet', 'Dr. Fatma']
        }
        
        medical_df = pd.DataFrame(medical_data)
        medical_df.to_excel('data/sample_lifestyle_data.xlsx', index=False)
        
        logger.info("Örnek veri dosyaları oluşturuldu")
        
        return genetic_df, medical_df
    
    def get_data_summary(self, df, data_type):
        """Veri özeti oluştur"""
        summary = {
            'data_type': data_type,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        return summary