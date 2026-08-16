import os
import sys
import pytest

# Add backend and ai_model src dirs to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai_model/src')))

from config import settings as config
from utils.preprocessing import clean_text
from services.robustness import inject_typos, add_distracting_text

def test_text_cleaning():
    """Test text cleaning preprocessing steps with anonymization."""
    # Test lowercase
    assert clean_text("HELLO WORLD") == "hello world"
    
    # Test URL removal
    assert clean_text("Check this out https://google.com links") == "check this out links"
    
    # Test HTML removal
    assert clean_text("<p>Hello</p> <b>World</b>") == "hello world"
    
    # Test reddit tags anonymization
    assert clean_text("post by u/test_user on r/test_sub") == "post by [user] on [subreddit]"
    
    # Test PII names masking
    assert clean_text("Hello, my name is John") == "hello my name is [name]"
    
    # Test special characters removal
    assert clean_text("I am feeling sad... !!!") == "i am feeling sad"

def test_config_paths():
    """Test configurations and directory mappings."""
    assert config.BASE_DIR is not None
    assert os.path.basename(config.DATA_DIR) == "data"
    assert os.path.basename(config.MODELS_DIR) == "models"

def test_robustness_perturbations():
    """Test text noise perturbation functions."""
    sample_text = "this is a very long sample sentence to test perturbations"
    
    # Typos should change spelling but preserve length or vocabulary size roughly
    typo_text = inject_typos(sample_text, rate=1.0)
    assert typo_text != sample_text
    
    # Distraction should append text
    distracted_text = add_distracting_text(sample_text)
    assert len(distracted_text) > len(sample_text)
    assert sample_text in distracted_text

def test_pii_anonymizer_direct():
    """Test the mask_pii function directly from anonymizer.py."""
    from services.anonymizer import mask_pii
    assert mask_pii("my email is test@example.com") == "my email is [EMAIL]"
    assert mask_pii("call me at 123-456-7890") == "call me at [PHONE]"
    assert mask_pii("this is Sarah") == "my name is [NAME]"
