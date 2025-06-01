# Otomasyon Kuralları

Bu doküman, Akıllı Ev Otomasyon Sistemi'nde kullanılan kural tabanlı otomasyonun yapısını, kurallarını ve çalışma prensiplerini detaylı olarak açıklamaktadır.

## Kural Motoru Genel Bakış

Otomasyon sistemi, sensör verilerini ve makine öğrenmesi tahminlerini kullanarak ev cihazlarını kontrol eden bir kural motoru içerir. Kural motoru, her bir kuralı belirli koşullara göre değerlendirir ve uygun eylemleri tetikler.

## Kural Yapısı

Her kural şu bileşenlerden oluşur:

1. **İsim:** Kuralı benzersiz olarak tanımlayan bir isim
2. **Koşul Fonksiyonu:** Mevcut durum bilgilerini alıp boolean bir değer döndüren fonksiyon
3. **Eylem Fonksiyonu:** Koşul sağlandığında yapılacak işlemleri tanımlayan fonksiyon
4. **Öncelik:** Kuralın öncelik seviyesi (çakışmaları çözmek için)
5. **Açıklama:** Kuralın amacını ve işleyişini açıklayan metin
6. **Durum:** Etkin/Devre Dışı durumu

## Temel Kural Seti

Sistem aşağıdaki temel kuralları içerir:

### 1. Sıcaklık Kontrolü

```python
def high_temperature_condition(state, devices):
    """Sıcaklık belirli bir eşiği geçerse True döndürür."""
    room = state.get("room")
    temp_col = f"{room}_Sıcaklık"
    if temp_col in state:
        return state[temp_col] > 26.0  # Sıcaklık 26°C'den yüksekse
    return False

def activate_cooling(state, devices):
    """Soğutma sistemini aktifleştirir."""
    room = state.get("room")
    ac_device = f"{room}_Klima"
    if ac_device in devices:
        devices[ac_device] = True
        return {ac_device: True}
    return {}

# Kural ekleme
rules_engine.add_rule(
    name="high_temp_cooling",
    condition_func=high_temperature_condition,
    action_func=activate_cooling,
    priority=1,
    description="Sıcaklık 26°C'yi geçtiğinde klimayı aç"
)
```

### 2. Boş Oda Aydınlatma Kontrolü

```python
def empty_room_lights_condition(state, devices):
    """Oda boş ve ışıklar açıksa True döndürür."""
    room = state.get("room")
    occupancy_col = f"{room}_Doluluk"
    light_device = f"{room}_Lamba"
    
    if occupancy_col in state and light_device in devices:
        return state[occupancy_col] == False and devices[light_device] == True
    return False

def turn_off_lights(state, devices):
    """Lambayı kapatır."""
    room = state.get("room")
    light_device = f"{room}_Lamba"
    if light_device in devices:
        devices[light_device] = False
        return {light_device: False}
    return {}

# Kural ekleme
rules_engine.add_rule(
    name="empty_room_lights_off",
    condition_func=empty_room_lights_condition,
    action_func=turn_off_lights,
    priority=2,
    description="Oda boş olduğunda ışıkları kapat"
)
```

### 3. Hava Kalitesi Kontrolü

```python
def poor_air_quality_condition(state, devices):
    """CO2 seviyesi eşiği aşarsa True döndürür."""
    room = state.get("room")
    co2_col = f"{room}_CO2"
    
    if co2_col in state:
        return state[co2_col] > 1000  # CO2 seviyesi 1000 ppm'den yüksekse
    return False

def activate_ventilation(state, devices):
    """Havalandırmayı aktifleştirir."""
    room = state.get("room")
    ventilation_device = f"{room}_Havalandırma"
    
    if ventilation_device in devices:
        devices[ventilation_device] = True
        return {ventilation_device: True}
    return {}

# Kural ekleme
rules_engine.add_rule(
    name="poor_air_ventilation",
    condition_func=poor_air_quality_condition,
    action_func=activate_ventilation,
    priority=1,
    description="CO2 seviyesi 1000 ppm'yi geçtiğinde havalandırmayı aç"
)
```

### 4. Gün Batımı Perde Kontrolü

```python
def sunset_condition(state, devices):
    """Akşam vakti ve yeterli ışık yoksa True döndürür."""
    current_time = state.get("timestamp")
    room = state.get("room")
    light_col = f"{room}_Işık"
    
    if current_time and light_col in state:
        hour = current_time.hour
        return 17 <= hour <= 21 and state[light_col] < 100  # Akşam 17-21 arası ve düşük ışık
    return False

def close_curtains(state, devices):
    """Perdeleri kapatır."""
    room = state.get("room")
    curtain_device = f"{room}_Perde"
    
    if curtain_device in devices:
        devices[curtain_device] = False  # False = Kapalı
        return {curtain_device: False}
    return {}

# Kural ekleme
rules_engine.add_rule(
    name="sunset_curtains",
    condition_func=sunset_condition,
    action_func=close_curtains,
    priority=3,
    description="Akşam vakti ve ışık azaldığında perdeleri kapat"
)
```

### 5. Sabah Rutini

```python
def morning_routine_condition(state, devices):
    """Sabah vakti ise True döndürür."""
    current_time = state.get("timestamp")
    
    if current_time:
        hour = current_time.hour
        return 7 <= hour <= 9  # Sabah 7-9 arası
    return False

def morning_routine_action(state, devices):
    """Sabah rutinini uygular: perdeleri aç, ısıyı ayarla."""
    room = state.get("room")
    changes = {}
    
    # Perdeleri aç
    curtain_device = f"{room}_Perde"
    if curtain_device in devices:
        devices[curtain_device] = True  # True = Açık
        changes[curtain_device] = True
    
    # Kış mevsiminde ısıtmayı aç (opsiyonel)
    # Bu örnekte mevsim kontrolü yapılmıyor, gerçek uygulamada eklenebilir
    temp_col = f"{room}_Sıcaklık"
    ac_device = f"{room}_Klima"
    if temp_col in state and ac_device in devices:
        if state[temp_col] < 20:  # 20°C'den düşükse
            devices[ac_device] = True
            changes[ac_device] = True
    
    return changes

# Kural ekleme
rules_engine.add_rule(
    name="morning_routine",
    condition_func=morning_routine_condition,
    action_func=morning_routine_action,
    priority=2,
    description="Sabah rutini: perdeleri aç, gerekirse ısıtmayı aç"
)
```

## Makine Öğrenmesi Entegrasyonu

Kural motoru, makine öğrenmesi tahminlerini de dikkate alır:

```python
def ml_prediction_condition(state, devices):
    """ML tahmini yeterince güvenliyse True döndürür."""
    device_name = state.get("current_device")
    predictions = state.get("ml_predictions", {})
    
    if device_name in predictions:
        confidence = predictions[device_name].get("probability", 0)
        return confidence > 0.7  # %70'den fazla güven varsa
    return False

def apply_ml_prediction(state, devices):
    """ML tahminini uygular."""
    device_name = state.get("current_device")
    predictions = state.get("ml_predictions", {})
    
    if device_name in predictions and device_name in devices:
        predicted_state = predictions[device_name].get("state")
        devices[device_name] = predicted_state
        return {device_name: predicted_state}
    return {}

# Kural ekleme
rules_engine.add_rule(
    name="ml_predictions",
    condition_func=ml_prediction_condition,
    action_func=apply_ml_prediction,
    priority=5,  # Yüksek öncelik
    description="Makine öğrenmesi tahminlerini yüksek güven durumunda uygula"
)
```

## Kural Değerlendirme Süreci

Kural motoru, tüm kuralları aşağıdaki süreçte değerlendirir:

1. **Durum Toplama:** Tüm sensörlerden güncel durum bilgisi toplanır
2. **Kural Filtreleme:** Aktif kurallar seçilir
3. **Öncelik Sıralama:** Kurallar önceliğe göre sıralanır
4. **Koşul Değerlendirme:** Her kuralın koşulu değerlendirilir
5. **Eylem Uygulama:** Koşulu sağlayan kuralların eylemleri uygulanır
6. **Çakışma Çözümü:** Çakışan eylemlerde yüksek öncelikli kurallar tercih edilir
7. **Cihaz Güncelleme:** Nihai cihaz durumları güncellenir
8. **Loglama:** Yapılan değişiklikler ve kararlar loglanır

## Kural Loglama Sistemi

Otomasyon kararları, detaylı bir şekilde loglanır ve analiz için kaydedilir:

```json
{
  "timestamp": "2025-05-27 14:32:15",
  "rule_name": "high_temp_cooling",
  "description": "Sıcaklık 26°C'yi geçtiğinde klimayı aç",
  "room": "Salon",
  "conditions": {
    "Salon_Sıcaklık": 27.5,
    "Salon_Doluluk": true
  },
  "before_state": {
    "Salon_Klima": false
  },
  "changes": {
    "Salon_Klima": true
  },
  "confidence": 1.0,
  "triggered_by": "rule_engine"
}
```

## Kullanıcı Önceliği

Kullanıcı manuel olarak bir cihazı kontrol ettiğinde, bu eylem kural motorunun kararlarından daha yüksek önceliğe sahiptir. Kullanıcı müdahaleleri kaydedilir ve gelecekte makine öğrenmesi modelinin eğitimi için kullanılır.

## Özelleştirme ve Genişletme

Kural motoru, yeni kurallar eklemek veya mevcut kuralları değiştirmek için esnek bir yapı sunar:

```python
# Yeni özel kural ekleme
def custom_condition(state, devices):
    # Özel koşul mantığı
    return condition_result

def custom_action(state, devices):
    # Özel eylem mantığı
    return changes

rules_engine.add_rule(
    name="custom_rule",
    condition_func=custom_condition,
    action_func=custom_action,
    priority=custom_priority,
    description="Özel kural açıklaması"
)
```

## Sonuç

Kural tabanlı otomasyon sistemi, akıllı ev sisteminin temel davranışlarını belirler ve makine öğrenmesi tahminleriyle entegre çalışır. Kurallar, ev sakinlerinin konforunu ve enerji verimliliğini maksimize edecek şekilde tasarlanmıştır ve ev sakinlerinin alışkanlıklarına göre zamanla gelişir.