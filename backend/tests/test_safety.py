import pytest
from ai.safety import check_for_emergency
from ai.severity import classify_risk_severity

def test_emergency_trigger_detection():
    # Test safe inputs
    assert check_for_emergency("I have a mild headache since yesterday.") == False
    assert check_for_emergency("My stomach hurts a little bit.") == False
    
    # Test high-risk trigger phrases
    assert check_for_emergency("I am experiencing severe chest pain right now.") == True
    assert check_for_emergency("My father just had a stroke.") == True
    assert check_for_emergency("I think I am having a heart attack.") == True
    assert check_for_emergency("There is severe bleeding from the wound.") == True
    
    # Test case insensitivity
    assert check_for_emergency("CHEST PAIN") == True
    assert check_for_emergency("I CAN'T breather properly.") == False # typo
    assert check_for_emergency("I can't breathe properly.") == True

def test_severity_classification():
    # Emergency always triggers High
    assert classify_risk_severity("chest pain", is_emergency=True) == "High"
    
    # Short safe text is Low
    assert classify_risk_severity("I have a small scrape on my knee.", is_emergency=False) == "Low"
    
    # Very long text (heuristic for complex symptoms) is Medium
    long_text = "I have been experiencing a persistent headache along with some mild nausea, random bouts of dizziness when standing up quickly, occasional tingling in my fingers, general fatigue that doesn't go away even after sleeping for eight full hours, and a slight sensitivity to bright lights in the morning."
    assert classify_risk_severity(long_text, is_emergency=False) == "Medium"
