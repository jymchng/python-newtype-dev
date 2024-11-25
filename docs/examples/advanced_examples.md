# Advanced Examples

## Method Interception
```python
from newtype import NewType
import time

class TimedDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.operation_times = {}
    
    def __getitem__(self, key):
        start = time.time()
        result = super().__getitem__(key)
        elapsed = time.time() - start
        self.operation_times[key] = elapsed
        return result
    
    def get_stats(self):
        return self.operation_times

# Usage
d = TimedDict()
d["key"] = "value"
_ = d["key"]
print(d.get_stats())  # Shows access times
```

## Custom Initialization with Validation
```python
from newtype import NewType
from typing import Optional

class EmailStr(NewType(str)):
    def __init__(self, value: str, strict: bool = True):
        if strict and '@' not in value:
            raise ValueError("Invalid email format")
        super().__init__()
    
    @property
    def domain(self) -> Optional[str]:
        if '@' in self:
            return self.split('@')[1]
        return None

# Usage
email = EmailStr("user@example.com")
print(email.domain)  # example.com
```

## Type with Context Management
```python
from newtype import NewType
import logging

class LoggedList(NewType(list)):
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)
    
    def __enter__(self):
        self.logger.info("Starting list operations")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Finished list operations")
        if exc_type:
            self.logger.error(f"Error occurred: {exc_val}")
        return False

# Usage
with LoggedList() as lst:
    lst.append(1)
    lst.extend([2, 3, 4])
```
