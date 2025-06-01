"""
Kural motoru modülü için birim testleri
"""
import pytest
from datetime import datetime
from src.automation.rules_engine import RulesEngine

class TestRulesEngine:
    """RulesEngine sınıfı için test sınıfı"""
    
    @pytest.fixture
    def engine(self):
        """Test için RulesEngine örneği oluşturur"""
        return RulesEngine()
    
    @pytest.fixture
    def current_state(self):
        """Test için örnek durum verisi"""
        return {
            'timestamp': datetime.now(),
            'Salon_Sıcaklık': 28.0,
            'Salon_Nem': 55.0,
            'Salon_CO2': 800,
            'Salon_Işık': 300,
            'Salon_Hareket': True,
            'Salon_Doluluk': True,
            'hour': 14,
            'is_weekend': 0
        }
    
    @pytest.fixture
    def devices(self):
        """Test için örnek cihaz durumları"""
        return {
            'Salon_Klima': False,
            'Salon_Lamba': True,
            'Salon_Perde': True,
            'Salon_Havalandırma': False
        }
    
    def test_add_rule(self, engine):
        """add_rule metodu doğru çalışıyor mu?"""
        # Test kuralı
        def test_condition(state, devices):
            return state.get('Salon_Sıcaklık', 0) > 25
        
        def test_action(state, devices):
            devices['Salon_Klima'] = True
            return devices
        
        # Kuralı ekle
        engine.add_rule(
            'test_rule',
            test_condition,
            test_action,
            priority=2,
            description='Test kuralı'
        )
        
        # Kural eklenmiş mi?
        assert 'test_rule' in [rule['name'] for rule in engine.rules]
        added_rule = next(rule for rule in engine.rules if rule['name'] == 'test_rule')
        assert added_rule['priority'] == 2
        assert added_rule['description'] == 'Test kuralı'
        assert added_rule['enabled'] is True
        assert added_rule['condition'] == test_condition
        assert added_rule['action'] == test_action
    
    def test_disable_enable_rule(self, engine):
        """disable_rule ve enable_rule metodları doğru çalışıyor mu?"""
        # Test kuralı ekle
        def test_condition(state, devices):
            return True
        
        def test_action(state, devices):
            return devices
        
        engine.add_rule('test_rule', test_condition, test_action)
        
        # Kuralı devre dışı bırak
        engine.disable_rule('test_rule')
        
        # Kural devre dışı mı?
        disabled_rule = next(rule for rule in engine.rules if rule['name'] == 'test_rule')
        assert disabled_rule['enabled'] is False
        
        # Kuralı tekrar etkinleştir
        engine.enable_rule('test_rule')
        
        # Kural etkin mi?
        enabled_rule = next(rule for rule in engine.rules if rule['name'] == 'test_rule')
        assert enabled_rule['enabled'] is True
    
    def test_evaluate_rules(self, engine, current_state, devices):
        """evaluate_rules metodu doğru çalışıyor mu?"""
        # Test kuralları
        def high_temp_condition(state, devices):
            return state.get('Salon_Sıcaklık', 0) > 26
        
        def high_temp_action(state, devices):
            devices['Salon_Klima'] = True
            return devices
        
        def motion_condition(state, devices):
            return not state.get('Salon_Hareket', False)
        
        def motion_action(state, devices):
            devices['Salon_Lamba'] = False
            return devices
        
        # Kuralları ekle
        engine.add_rule('high_temp', high_temp_condition, high_temp_action, priority=1)
        engine.add_rule('no_motion', motion_condition, motion_action, priority=2)
        
        # Kuralları değerlendir
        updated_devices = engine.evaluate_rules(current_state, devices)
        
        # Doğru kurallar tetiklendi mi?
        assert updated_devices['Salon_Klima'] is True  # high_temp kuralı tetiklendi
        assert updated_devices['Salon_Lamba'] is True  # no_motion kuralı tetiklenmedi (hareket var)