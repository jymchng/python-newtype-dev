# Real-World Use Cases

## Configuration Management
```python
from newtype import NewType
import json
from pathlib import Path

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
        self.save()  # Auto-save on changes

# Usage
config = ConfigDict("app_config.json")
config["api_key"] = "secret123"  # Automatically saves to file
```

## Data Validation
```python
from newtype import NewType
from typing import Any, Dict
import re

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

# Usage
schema = {
    'email': {'type': str, 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'},
    'age': {'type': int},
}

user_data = ValidatedDict(schema)
user_data['email'] = 'user@example.com'  # Valid
user_data['age'] = 25                    # Valid
user_data['email'] = 'invalid'           # Raises ValueError
```

## Audit Logging
```python
from newtype import NewType
from datetime import datetime
import json

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

# Usage
audit_dict = AuditedDict()
audit_dict['user'] = 'admin'  # Logs the operation
del audit_dict['user']        # Logs the deletion
```
