# moresso  

A lightweight and extensible Single Sign-On (SSO) authentication library for Python.  

This package provides:  

- ✅ RS256 JWT validation using a public key from a URL  
- ✅ In-memory caching for public keys  
- ✅ Header-based decorator (`@auth_required`)  
- ✅ AWS Lambda and FastAPI-ready  
- ✅ Configurable via environment variables or programmatic init  
- ✅ Extensible permission system (`BasePermission` → custom rules)  

---

## Installation  

```bash
pip install moresso
```
Configuration
You can configure the package either programmatically or via environment variables.

Method 1: Programmatic init
from more_sso import init_sso_config
```python
init_sso_config(
    public_key_uri="https://auth.more.in/public_key",
    audience="my-service"
    )
```
Method 2: Environment variables
```bash
export PUBLIC_KEY_URI="https://auth.more.in/public_key"
export AUDIENCE="my-service"
```

Usage
1. Decorator-based Authorization
The decoded JWT payload is automatically injected into the headers["user"].
```python
from more_sso import auth_required
@auth_required(permission="scopes.store_ids", value=1108)
def my_func(event, *args, **kwargs):
    user = event.get("requestContext", {}).get("user")
    print("User:", user)
    return {"ok": True}

```
2. Token Validation in Code
You can also validate JWT tokens directly.
```python
from more_sso import validate_token
from more_sso import JWTValidationError
try:
    user = validate_token(token)
    print(user)
except JWTValidationError as e:
    print("Invalid token:", str(e))
```
3. Root-Level Authorization (AWS Lambda)
The decoded payload is injected into event["requestContext"]["user"].
```python
from more_sso import root_auth_required
@root_auth_required
def lambda_handler(event, context):
    """If authentication fails, it returns statusCode 401 automatically"""
    user = event["requestContext"]["user"]
    return {"statusCode": 200, "body": f"Hello {user['sub']}"}
```
Permissions
The default JSONPermissionChecker lets you enforce JSON-based policies (nested claims, lists, or flags).
Example:
```python
@auth_required(permission="scopes.store_ids", value=1101)
def handler(event, *args, **kwargs):
    user = event['requestContext'].get("user", {})
    ...
```
This will check if the JWT contains:
```json
"permissions": {
  "store_id":  [1101, 1108]
}
```
Custom Permission Classes
You can define your own Permission checker by extending BasePermission:
```python
from more_sso import BasePermission
class CustomPermission(BasePermission):
    def has_access(self) -> bool:
        # Example: allow only admins
        return self.user.get("role") == "admin"

```
Use it in the decorator:
```python
@auth_required(permission_class=CustomPermission)
def admin_only(event, *args, **kwargs):
    return {"ok": "admin access granted"}
```
Exception Handling
```python
from more_sso import JWTValidationError
try:
    user = validate_token(token)
except JWTValidationError:
    return {"statusCode": 401, "body": "Unauthorized"}
```
Project Links

📦 PyPI: moresso

💻 Source Code: GitHub – [more-retail/moresso](https://github.com/more-retail/moresso)

License
MIT License.

