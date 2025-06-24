#!/usr/bin/env python3
"""
Proje için UML ve sistem diyagramları oluşturan script
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import numpy as np
import os

# Türkçe karakter desteği için font ayarı
plt.rcParams['font.family'] = 'DejaVu Sans'

def create_project_flow_diagram():
    """Şekil 1.1. Proje genel akış şeması"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define boxes
    boxes = [
        {'xy': (1, 8), 'width': 2, 'height': 1, 'text': 'Veri Toplama\n(Sensör Simülasyonu)', 'color': 'lightblue'},
        {'xy': (4, 8), 'width': 2, 'height': 1, 'text': 'Veri İşleme\n(Preprocessing)', 'color': 'lightgreen'},
        {'xy': (7, 8), 'width': 2, 'height': 1, 'text': 'Model Eğitimi\n(Random Forest)', 'color': 'lightyellow'},
        {'xy': (1, 5.5), 'width': 2, 'height': 1, 'text': 'Cihaz Kontrolü\n(Otomasyon)', 'color': 'lightcoral'},
        {'xy': (4, 5.5), 'width': 2, 'height': 1, 'text': 'Enerji Analizi\n(Optimizasyon)', 'color': 'lightpink'},
        {'xy': (7, 5.5), 'width': 2, 'height': 1, 'text': 'Raporlama\n(Visualization)', 'color': 'lavender'},
        {'xy': (4, 3), 'width': 2, 'height': 1, 'text': 'Kullanıcı Arayüzü\n(Interactive)', 'color': 'lightgray'}
    ]
    
    # Draw boxes
    for box in boxes:
        rect = FancyBboxPatch(box['xy'], box['width'], box['height'],
                             boxstyle='round,pad=0.1', facecolor=box['color'],
                             edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2,
               box['text'], ha='center', va='center', fontsize=10, weight='bold')
    
    # Draw arrows
    arrows = [
        ((3, 8.5), (4, 8.5)),
        ((6, 8.5), (7, 8.5)),
        ((2, 8), (2, 6.5)),
        ((5, 8), (5, 6.5)),
        ((8, 8), (8, 6.5)),
        ((5, 5.5), (5, 4))
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))
    
    plt.title('Şekil 1.1. Proje Genel Akış Şeması', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/project_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Proje akış şeması oluşturuldu!')

def create_system_block_diagram():
    """Şekil 2.1. Sistem blok diyagramı"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Katmanlar
    layers = [
        {'xy': (1, 8), 'width': 10, 'height': 1.5, 'text': 'Kullanıcı Arayüzü Katmanı\n(Interactive Interface)', 'color': 'lightsteelblue'},
        {'xy': (1, 6), 'width': 10, 'height': 1.5, 'text': 'Otomasyon Motoru Katmanı\n(Automation Engine)', 'color': 'lightgreen'},
        {'xy': (1, 4), 'width': 10, 'height': 1.5, 'text': 'Makine Öğrenmesi Katmanı\n(ML Processing Layer)', 'color': 'lightyellow'},
        {'xy': (1, 2), 'width': 10, 'height': 1.5, 'text': 'Veri Katmanı\n(Data Simulation & Storage)', 'color': 'lightcoral'},
        {'xy': (1, 0.2), 'width': 10, 'height': 1.5, 'text': 'Sensör & Cihaz Simülasyon Katmanı\n(Hardware Abstraction)', 'color': 'lavender'}
    ]
    
    for layer in layers:
        rect = FancyBboxPatch(layer['xy'], layer['width'], layer['height'],
                             boxstyle='round,pad=0.1', facecolor=layer['color'],
                             edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(layer['xy'][0] + layer['width']/2, layer['xy'][1] + layer['height']/2,
               layer['text'], ha='center', va='center', fontsize=11, weight='bold')
    
    # Oklar (katmanlar arası)
    arrow_positions = [7.5, 5.5, 3.5, 1.5]
    for i in range(len(arrow_positions)-1):
        ax.annotate('', xy=(6, arrow_positions[i+1]), xytext=(6, arrow_positions[i]),
                    arrowprops=dict(arrowstyle='<->', lw=3, color='red'))
    
    plt.title('Şekil 2.1. Sistem Blok Diyagramı (Katmanlı Mimari)', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/system_block_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Sistem blok diyagramı oluşturuldu!')

def create_data_flow_diagram():
    """Şekil 2.2. Veri akış şeması (DFD)"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Veri işlem kutuları
    processes = [
        {'xy': (1, 8), 'width': 2, 'height': 1, 'text': 'Sensör Veri\nÜretimi', 'color': 'lightblue'},
        {'xy': (5, 8), 'width': 2, 'height': 1, 'text': 'Veri\nDoğrulama', 'color': 'lightgreen'},
        {'xy': (9, 8), 'width': 2, 'height': 1, 'text': 'Özellik\nÇıkarımı', 'color': 'lightyellow'},
        {'xy': (1, 5), 'width': 2, 'height': 1, 'text': 'Model\nEğitimi', 'color': 'lightcoral'},
        {'xy': (5, 5), 'width': 2, 'height': 1, 'text': 'Tahmin\nMotoru', 'color': 'lightpink'},
        {'xy': (9, 5), 'width': 2, 'height': 1, 'text': 'Cihaz\nKontrolü', 'color': 'lavender'},
        {'xy': (5, 2), 'width': 2, 'height': 1, 'text': 'Performans\nİzleme', 'color': 'lightgray'}
    ]
    
    # Veri depoları (dikdörtgen)
    storages = [
        {'xy': (3.5, 6.5), 'width': 3, 'height': 0.8, 'text': 'Ham Veri\n(Raw Data)', 'color': 'wheat'},
        {'xy': (7.5, 6.5), 'width': 3, 'height': 0.8, 'text': 'İşlenmiş Veri\n(Processed Data)', 'color': 'wheat'},
        {'xy': (3.5, 3.5), 'width': 3, 'height': 0.8, 'text': 'Model Deposu\n(Model Storage)', 'color': 'wheat'}
    ]
    
    # İşlemleri çiz
    for proc in processes:
        circle = Circle((proc['xy'][0] + proc['width']/2, proc['xy'][1] + proc['height']/2), 
                       proc['width']/2, facecolor=proc['color'], edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        ax.text(proc['xy'][0] + proc['width']/2, proc['xy'][1] + proc['height']/2,
               proc['text'], ha='center', va='center', fontsize=9, weight='bold')
    
    # Veri depolarını çiz
    for storage in storages:
        rect = Rectangle(storage['xy'], storage['width'], storage['height'],
                        facecolor=storage['color'], edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(storage['xy'][0] + storage['width']/2, storage['xy'][1] + storage['height']/2,
               storage['text'], ha='center', va='center', fontsize=9, weight='bold')
    
    # Veri akış okları
    flows = [
        ((3, 8.5), (5, 8.5)),  # Sensör -> Doğrulama
        ((7, 8.5), (9, 8.5)),  # Doğrulama -> Özellik
        ((6, 8), (5, 7.3)),    # Doğrulama -> Ham Veri
        ((9, 7.3), (9, 6.3)),  # Özellik -> İşlenmiş Veri
        ((8.5, 6.5), (3, 5.5)), # İşlenmiş Veri -> Model Eğitimi
        ((3, 5), (5, 5)),      # Model Eğitimi -> Tahmin
        ((7, 5), (9, 5)),      # Tahmin -> Kontrol
        ((6, 5), (6, 3)),      # Tahmin -> Performans
        ((2, 5), (5, 4.3))     # Model Eğitimi -> Model Deposu
    ]
    
    for start, end in flows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))
    
    plt.title('Şekil 2.2. Veri Akış Şeması (DFD)', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/data_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Veri akış şeması oluşturuldu!')

def create_uml_class_diagram():
    """Şekil 3.1. UML Sınıf diyagramı"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Sınıf kutuları
    classes = [
        {
            'xy': (1, 9), 'width': 3, 'height': 2.5, 
            'name': 'SmartHomeSimulator',
            'attributes': ['- sensors: List[Sensor]', '- devices: List[Device]', '- model_manager: MLModelManager'],
            'methods': ['+ run_simulation()', '+ generate_data()', '+ train_models()'],
            'color': 'lightblue'
        },
        {
            'xy': (6, 9), 'width': 3, 'height': 2.5,
            'name': 'SensorSimulator', 
            'attributes': ['- sensor_type: str', '- location: str', '- noise_level: float'],
            'methods': ['+ generate_data()', '+ add_noise()', '+ validate_reading()'],
            'color': 'lightgreen'
        },
        {
            'xy': (11, 9), 'width': 3, 'height': 2.5,
            'name': 'DeviceManager',
            'attributes': ['- devices: Dict', '- automation_rules: List'],
            'methods': ['+ control_device()', '+ apply_automation()', '+ get_energy_usage()'],
            'color': 'lightyellow'
        },
        {
            'xy': (1, 5.5), 'width': 3, 'height': 2.5,
            'name': 'MLModelManager',
            'attributes': ['- models: Dict', '- preprocessor: object', '- performance_data: List'],
            'methods': ['+ train_models()', '+ predict()', '+ evaluate_performance()'],
            'color': 'lightcoral'
        },
        {
            'xy': (6, 5.5), 'width': 3, 'height': 2.5,
            'name': 'AutomationEngine',
            'attributes': ['- rules: List[Rule]', '- scheduler: Scheduler'],
            'methods': ['+ execute_rules()', '+ schedule_tasks()', '+ optimize_energy()'],
            'color': 'lightpink'
        },
        {
            'xy': (11, 5.5), 'width': 3, 'height': 2.5,
            'name': 'DataProcessor',
            'attributes': ['- raw_data: DataFrame', '- processed_data: DataFrame'],
            'methods': ['+ clean_data()', '+ feature_engineering()', '+ split_data()'],
            'color': 'lavender'
        },
        {
            'xy': (3.5, 2), 'width': 3, 'height': 2.5,
            'name': 'HomeDataGenerator',
            'attributes': ['- num_rooms: int', '- residents: int', '- simulation_days: int'],
            'methods': ['+ generate_dataset()', '+ save_to_csv()', '+ create_scenarios()'],
            'color': 'wheat'
        },
        {
            'xy': (8.5, 2), 'width': 3, 'height': 2.5,
            'name': 'InteractiveSimulation',
            'attributes': ['- simulator: SmartHomeSimulator', '- user_inputs: Dict'],
            'methods': ['+ start_interactive()', '+ handle_user_input()', '+ display_results()'],
            'color': 'lightgray'
        }
    ]
    
    # Sınıfları çiz
    for cls in classes:
        # Ana kutu
        rect = Rectangle(cls['xy'], cls['width'], cls['height'],
                        facecolor=cls['color'], edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        
        # Sınıf adı
        ax.text(cls['xy'][0] + cls['width']/2, cls['xy'][1] + cls['height'] - 0.3,
               cls['name'], ha='center', va='center', fontsize=10, weight='bold')
        
        # Çizgi
        ax.plot([cls['xy'][0], cls['xy'][0] + cls['width']], 
               [cls['xy'][1] + cls['height'] - 0.6, cls['xy'][1] + cls['height'] - 0.6], 
               'k-', linewidth=1)
        
        # Attributes
        y_offset = cls['height'] - 1
        for attr in cls['attributes']:
            ax.text(cls['xy'][0] + 0.1, cls['xy'][1] + y_offset,
                   attr, ha='left', va='center', fontsize=8)
            y_offset -= 0.3
        
        # Çizgi
        ax.plot([cls['xy'][0], cls['xy'][0] + cls['width']], 
               [cls['xy'][1] + y_offset + 0.1, cls['xy'][1] + y_offset + 0.1], 
               'k-', linewidth=1)
        
        # Methods
        for method in cls['methods']:
            ax.text(cls['xy'][0] + 0.1, cls['xy'][1] + y_offset,
                   method, ha='left', va='center', fontsize=8)
            y_offset -= 0.3
    
    # İlişki okları
    relationships = [
        ((2.5, 9), (2.5, 8)),           # SmartHomeSimulator -> MLModelManager
        ((4, 10.2), (6, 10.2)),         # SmartHomeSimulator -> SensorSimulator
        ((4, 9.8), (11, 9.8)),          # SmartHomeSimulator -> DeviceManager
        ((2.5, 5.5), (6, 6.8)),         # MLModelManager -> AutomationEngine
        ((9, 6.8), (11, 6.8)),          # AutomationEngine -> DeviceManager
        ((12.5, 5.5), (12.5, 8)),       # DataProcessor -> DeviceManager
        ((5, 3.5), (2.5, 5.5)),         # HomeDataGenerator -> MLModelManager
        ((10, 3.5), (7.5, 5.5))         # InteractiveSimulation -> AutomationEngine
    ]
    
    for start, end in relationships:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    
    plt.title('Şekil 3.1. UML Sınıf Diyagramı', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/uml_class_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ UML sınıf diyagramı oluşturuldu!')

def create_use_case_diagram():
    """Şekil 3.2. UML Kullanım durumu diyagramı"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Aktörler
    actors = [
        {'xy': (1, 8), 'text': 'Sistem\nYöneticisi'},
        {'xy': (1, 5), 'text': 'Ev\nSakini'},
        {'xy': (12, 6.5), 'text': 'Makine Öğrenmesi\nSistemi'}
    ]
    
    # Use case'ler (oval)
    use_cases = [
        {'center': (6, 8.5), 'width': 2.5, 'height': 0.8, 'text': 'Simülasyon\nÇalıştır'},
        {'center': (9, 8.5), 'width': 2.5, 'height': 0.8, 'text': 'Model\nEğit'},
        {'center': (6, 7), 'width': 2.5, 'height': 0.8, 'text': 'Veri\nAnaliz Et'},
        {'center': (9, 7), 'width': 2.5, 'height': 0.8, 'text': 'Performans\nDeğerlendir'},
        {'center': (6, 5.5), 'width': 2.5, 'height': 0.8, 'text': 'Cihaz\nKontrol Et'},
        {'center': (9, 5.5), 'width': 2.5, 'height': 0.8, 'text': 'Enerji\nOptimize Et'},
        {'center': (6, 4), 'width': 2.5, 'height': 0.8, 'text': 'Interaktif\nSimülasyon'},
        {'center': (9, 4), 'width': 2.5, 'height': 0.8, 'text': 'Rapor\nGörüntüle'},
        {'center': (7.5, 2.5), 'width': 2.5, 'height': 0.8, 'text': 'Ayarları\nYönet'}
    ]
    
    # Sistem sınırı
    system_boundary = Rectangle((4.5, 1.5), 6, 8, fill=False, edgecolor='black', linewidth=2, linestyle='--')
    ax.add_patch(system_boundary)
    ax.text(7.5, 9.7, 'Akıllı Ev Otomasyon Sistemi', ha='center', va='center', fontsize=12, weight='bold')
    
    # Aktörleri çiz
    for actor in actors:
        # Stick figure
        ax.plot(actor['xy'][0], actor['xy'][1] + 0.3, 'ko', markersize=8)  # Head
        ax.plot([actor['xy'][0], actor['xy'][0]], [actor['xy'][1], actor['xy'][1] + 0.3], 'k-', linewidth=2)  # Body
        ax.plot([actor['xy'][0] - 0.2, actor['xy'][0] + 0.2], [actor['xy'][1] + 0.15, actor['xy'][1] + 0.15], 'k-', linewidth=2)  # Arms
        ax.plot([actor['xy'][0] - 0.15, actor['xy'][0]], [actor['xy'][1] - 0.2, actor['xy'][1]], 'k-', linewidth=2)  # Left leg
        ax.plot([actor['xy'][0] + 0.15, actor['xy'][0]], [actor['xy'][1] - 0.2, actor['xy'][1]], 'k-', linewidth=2)  # Right leg
        
        ax.text(actor['xy'][0], actor['xy'][1] - 0.5, actor['text'], ha='center', va='center', fontsize=9, weight='bold')
    
    # Use case'leri çiz (oval)
    for uc in use_cases:
        from matplotlib.patches import Ellipse
        ellipse = Ellipse(uc['center'], uc['width'], uc['height'],
                         facecolor='lightyellow', edgecolor='black', linewidth=1)
        ax.add_patch(ellipse)
        ax.text(uc['center'][0], uc['center'][1], uc['text'], ha='center', va='center', fontsize=9, weight='bold')
    
    # İlişkiler
    connections = [
        # Sistem Yöneticisi
        ((1.5, 8), (5, 8.5)),    # Simülasyon Çalıştır
        ((1.5, 8), (8, 8.5)),    # Model Eğit
        ((1.5, 8), (5, 7)),      # Veri Analiz Et
        ((1.5, 8), (8, 7)),      # Performans Değerlendir
        
        # Ev Sakini
        ((1.5, 5), (5, 5.5)),    # Cihaz Kontrol Et
        ((1.5, 5), (5, 4)),      # Interaktif Simülasyon
        ((1.5, 5), (8, 4)),      # Rapor Görüntüle
        ((1.5, 5), (7, 2.5)),    # Ayarları Yönet
        
        # ML Sistemi
        ((11.5, 6.5), (8.5, 8.5)),  # Model Eğit
        ((11.5, 6.5), (8.5, 5.5))   # Enerji Optimize Et
    ]
    
    for start, end in connections:
        ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', linewidth=1)
    
    plt.title('Şekil 3.2. UML Kullanım Durumu Diyagramı', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/uml_use_case_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ UML kullanım durumu diyagramı oluşturuldu!')

def create_er_diagram():
    """Şekil 3.3. Veritabanı ER diyagramı"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Entities (dikdörtgen)
    entities = [
        {
            'xy': (1, 7), 'width': 2.5, 'height': 2,
            'name': 'SENSOR_DATA',
            'attributes': ['id (PK)', 'timestamp', 'sensor_type', 'location', 'value', 'unit'],
            'color': 'lightblue'
        },
        {
            'xy': (5.5, 7), 'width': 2.5, 'height': 2,
            'name': 'DEVICE_STATUS', 
            'attributes': ['id (PK)', 'device_id', 'timestamp', 'status', 'power_consumption'],
            'color': 'lightgreen'
        },
        {
            'xy': (10, 7), 'width': 2.5, 'height': 2,
            'name': 'AUTOMATION_LOGS',
            'attributes': ['id (PK)', 'timestamp', 'rule_id', 'action', 'result'],
            'color': 'lightyellow'
        },
        {
            'xy': (1, 3.5), 'width': 2.5, 'height': 2,
            'name': 'ENERGY_CONSUMPTION',
            'attributes': ['id (PK)', 'timestamp', 'device_id', 'energy_kwh', 'cost'],
            'color': 'lightcoral'
        },
        {
            'xy': (5.5, 3.5), 'width': 2.5, 'height': 2,
            'name': 'ML_MODELS',
            'attributes': ['id (PK)', 'model_name', 'algorithm', 'accuracy', 'created_date'],
            'color': 'lightpink'
        },
        {
            'xy': (10, 3.5), 'width': 2.5, 'height': 2,
            'name': 'DEVICES',
            'attributes': ['id (PK)', 'name', 'type', 'location', 'max_power'],
            'color': 'lavender'
        }
    ]
    
    # Entities çiz
    for entity in entities:
        rect = Rectangle(entity['xy'], entity['width'], entity['height'],
                        facecolor=entity['color'], edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Entity name
        ax.text(entity['xy'][0] + entity['width']/2, entity['xy'][1] + entity['height'] - 0.3,
               entity['name'], ha='center', va='center', fontsize=10, weight='bold')
        
        # Attributes
        y_offset = entity['height'] - 0.8
        for attr in entity['attributes']:
            ax.text(entity['xy'][0] + 0.1, entity['xy'][1] + y_offset,
                   attr, ha='left', va='center', fontsize=8)
            y_offset -= 0.25
    
    # Relationships (elmas şekli)
    relationships = [
        {'center': (4.2, 8), 'width': 1.2, 'height': 0.8, 'name': 'monitors', 'color': 'yellow'},
        {'center': (8.2, 8), 'width': 1.2, 'height': 0.8, 'name': 'controls', 'color': 'yellow'},
        {'center': (4.2, 4.5), 'width': 1.2, 'height': 0.8, 'name': 'consumes', 'color': 'yellow'},
        {'center': (8.2, 4.5), 'width': 1.2, 'height': 0.8, 'name': 'uses', 'color': 'yellow'}
    ]
    
    # Relationships çiz (elmas)
    for rel in relationships:
        # Elmas şekli koordinatları
        diamond_x = [rel['center'][0], rel['center'][0] + rel['width']/2, 
                    rel['center'][0], rel['center'][0] - rel['width']/2]
        diamond_y = [rel['center'][1] + rel['height']/2, rel['center'][1], 
                    rel['center'][1] - rel['height']/2, rel['center'][1]]
        
        ax.fill(diamond_x, diamond_y, facecolor=rel['color'], edgecolor='black', linewidth=1)
        ax.text(rel['center'][0], rel['center'][1], rel['name'], 
               ha='center', va='center', fontsize=8, weight='bold')
    
    # Bağlantı çizgileri
    connections = [
        # SENSOR_DATA - monitors - DEVICE_STATUS
        ((3.5, 8), (4.2, 8)),
        ((4.2, 8), (5.5, 8)),
        
        # DEVICE_STATUS - controls - AUTOMATION_LOGS
        ((8, 8), (8.2, 8)),
        ((8.2, 8), (10, 8)),
        
        # ENERGY_CONSUMPTION - consumes - ML_MODELS
        ((3.5, 4.5), (4.2, 4.5)),
        ((4.2, 4.5), (5.5, 4.5)),
        
        # ML_MODELS - uses - DEVICES
        ((8, 4.5), (8.2, 4.5)),
        ((8.2, 4.5), (10, 4.5)),
        
        # Vertical connections
        ((2.25, 7), (2.25, 5.5)),    # SENSOR_DATA - ENERGY_CONSUMPTION
        ((6.75, 7), (6.75, 5.5)),    # DEVICE_STATUS - ML_MODELS
        ((11.25, 7), (11.25, 5.5))   # AUTOMATION_LOGS - DEVICES
    ]
    
    for start, end in connections:
        ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', linewidth=2)
    
    plt.title('Şekil 3.3. Veritabanı ER Diyagramı', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('reports/figures/er_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Veritabanı ER diyagramı oluşturuldu!')

def main():
    """Tüm diyagramları oluştur"""
    print("🎨 Proje diyagramları oluşturuluyor...")
    
    # Klasörü kontrol et ve oluştur
    os.makedirs('reports/figures', exist_ok=True)
    
    # Diyagramları oluştur
    create_project_flow_diagram()
    create_system_block_diagram()
    create_data_flow_diagram()
    create_uml_class_diagram()
    create_use_case_diagram()
    create_er_diagram()
    
    print("\n🎉 Tüm diyagramlar başarıyla oluşturuldu!")
    print("📁 Dosyalar: reports/figures/ klasöründe")

if __name__ == "__main__":
    main()
