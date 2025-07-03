 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MYP Sağlık Yapay Zeka Sistemi - Ana Başlatıcı
Bu yazılım Mehmet Yay tarafından geliştirilmiştir. Tüm hakları saklıdır.
Yapay zeka destekli olsa bile bu proje dışarıdan hiçbir katkı almamıştır.
Kodların, görsellerin ve veritabanlarının tüm hakları Mehmet Yay'a aittir.
İzinsiz kopyalanamaz, dağıtılamaz, satılamaz.
"""

import sys
import os
import logging
from pathlib import Path



# Proje kök dizinini ayarla
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Gerekli klasörleri oluştur
required_dirs = [
    'modules', 'data', 'data/languages', 'assets', 'assets/icons', 
    'assets/styles', 'assets/fonts', 'utils', 'docs', 'outputs'
]

for dir_name in required_dirs:
    dir_path = PROJECT_ROOT / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/myp_health_ai.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('MYP_HEALTH_AI')

def check_dependencies():
    import importlib

    import_names = {
        'PyQt5': 'PyQt5',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'openpyxl': 'openpyxl',
        'reportlab': 'reportlab',
        'nltk': 'nltk',
        'sqlite3': 'sqlite3'
    }

    missing_packages = []
    for pip_name, import_name in import_names.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"❌ Eksik kütüphaneler: {', '.join(missing_packages)}")
        print("📦 Kurulum için: pip install -r requirements.txt")
        return False
    return True

def main():
    """Ana uygulama başlatıcısı"""
    print("🏥 MYP Sağlık Yapay Zeka Sistemi Başlatılıyor...")
    print("👨‍💻 Geliştirici: Mehmet Yay")
    print("🔒 Tüm hakları saklıdır - Offline Sağlık AI Sistemi")
    print("-" * 60)
    
    # Bağımlılıkları kontrol et
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Ana UI modülünü import et ve başlat
        from modules.MYP_ui import HealthAIApplication
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("MYP Sağlık AI")
        app.setApplicationVersion("1.0.0")
        
        # Ana pencereyi oluştur ve göster
        main_window = HealthAIApplication()
        main_window.show()
        
        logger.info("MYP Sağlık AI Sistemi başarıyla başlatıldı")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Sistem başlatılırken hata oluştu: {str(e)}")
        print(f"❌ Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()