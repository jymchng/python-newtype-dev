import pytest
import json
import tempfile
from pathlib import Path
from newtype import NewType
from typing import Any, Dict
import re
from datetime import datetime


def test_config_dict():
    class ConfigDict(NewType(dict)):
        def __init__(self, config_file: str = "config.json"):
            super().__init__()
            self.config_file = Path(config_file)
            if self.config_file.exists():
                self.load()
        
        def load(self):
            with open(self.config_file) as f:
                self.update(json.load(f))
        
        def save(self):
            with open(self.config_file, 'w') as f:
                json.dump(self, f, indent=2)
        
        def __setitem__(self, key, value):
            super().__setitem__(key, value)
            self.save()
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as temp_file:
        config_path = temp_file.name
        configs = {
            "api_key": "secret123",
            "debug": True,
        }
        json.dump(configs, temp_file)
    
    try:
       
        # Test loading configuration
        new_config = ConfigDict(config_path)
        assert new_config["api_key"] == "secret123"
        assert new_config["debug"] is True
        
        # Test updating configuration
        new_config["api_key"] = "new_secret"
        another_config = ConfigDict(config_path)
        assert another_config["api_key"] == "new_secret"
    
    finally:
        # Cleanup
        Path(config_path).unlink()


def test_validated_dict():
    class ValidatedDict(NewType(dict)):
        def __init__(self, schema: Dict[str, Any]):
            super().__init__()
            self.schema = schema
        
        def __setitem__(self, key: str, value: Any):
            if key not in self.schema:
                raise KeyError(f"Key '{key}' not in schema")
            
            expected_type = self.schema[key].get('type')
            if not isinstance(value, expected_type):
                raise TypeError(f"Value for '{key}' must be {expected_type}")
            
            pattern = self.schema[key].get('pattern')
            if pattern and isinstance(value, str):
                if not re.match(pattern, value):
                    raise ValueError(f"Value for '{key}' doesn't match pattern {pattern}")
            
            super().__setitem__(key, value)
    
    schema = {
        'email': {'type': str, 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'},
        'age': {'type': int},
        'name': {'type': str, 'pattern': r'^[a-zA-Z\s]+$'}
    }
    
    data = ValidatedDict(schema)
    
    # Test valid data
    data['email'] = 'user@example.com'
    data['age'] = 25
    data['name'] = 'John Doe'
    
    # Test invalid key
    with pytest.raises(KeyError):
        data['invalid_key'] = 'value'
    
    # Test invalid type
    with pytest.raises(TypeError):
        data['age'] = '25'  # string instead of int
    
    # Test invalid pattern
    with pytest.raises(ValueError):
        data['email'] = 'invalid_email'
    
    with pytest.raises(ValueError):
        data['name'] = 'John123'  # contains numbers


def test_audited_dict():
    class AuditedDict(NewType(dict)):
        def __init__(self, audit_file: str = "audit.log"):
            super().__init__()
            self.audit_file = audit_file
        
        def _log_operation(self, operation: str, key: str, value: Any = None):
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'key': key,
                'value': value
            }
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        def __setitem__(self, key, value):
            self._log_operation('set', key, value)
            super().__setitem__(key, value)
        
        def __delitem__(self, key):
            self._log_operation('delete', key)
            super().__delitem__(key)
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp_file:
        audit_path = temp_file.name
    
    try:
        audit_dict = AuditedDict(audit_path)
        
        # Test setting items
        audit_dict['user'] = 'admin'
        audit_dict['role'] = 'superuser'
        
        # Test deleting items
        del audit_dict['role']
        
        # Verify audit log
        with open(audit_path) as f:
            log_lines = f.readlines()
        
        # Should have 3 log entries (2 sets and 1 delete)
        assert len(log_lines) == 3
        
        # Parse and verify log entries
        logs = [json.loads(line) for line in log_lines]
        
        assert logs[0]['operation'] == 'set'
        assert logs[0]['key'] == 'user'
        assert logs[0]['value'] == 'admin'
        
        assert logs[1]['operation'] == 'set'
        assert logs[1]['key'] == 'role'
        assert logs[1]['value'] == 'superuser'
        
        assert logs[2]['operation'] == 'delete'
        assert logs[2]['key'] == 'role'
        
        # Verify dictionary state
        assert 'user' in audit_dict
        assert 'role' not in audit_dict
        assert len(audit_dict) == 1
    
    finally:
        # Cleanup
        Path(audit_path).unlink()
