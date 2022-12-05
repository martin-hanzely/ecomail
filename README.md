# ecomail

Python wrapper for [ecomail.cz](https://www.ecomail.cz/) api.

## Quick start

1. Create `EcoMailOptions` instance:
   ```python
   from ecomail.service import EcoMailOptions
    
   options = EcoMailOptions(
        base_url="https://www.example.com/",  # Must end with trailing slash.
        api_key="123_mock_key",
   )
   ```
2. Create `EcoMailService` instance:
   ```python
   from ecomail.service import EcoMailService
    
   service = EcoMailService(options=options)
   ```

## Available endpoints:

### Add new list:
```python
list_id: int = service.add_new_list(
    name="List name",
    from_name="Organisation Name",
    from_email="organisation@example.com",
    reply_to="optional@example.com",
)
```

### Add new subscriber to list:
```python
from ecomail.subscriber import Subscriber

subscriber = Subscriber(
    name="John",
    surname="Doe",
    email="user@example.com",
)

subscriber_id: int = service.add_new_subscriber_to_list(
    list_id=123,
    subscriber=subscriber,
)
```

### Add bulk subscribers to list:
```python
from ecomail.subscriber import Subscriber

subscriber = Subscriber(
    name="John",
    surname="Doe",
    email="user@example.com",
)

# No return value.
service.add_bulk_subscribers_to_list(
    list_id=123,
    subscribers=[subscriber],
)
```
