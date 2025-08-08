# sso-auth

This package provides:

- RS256 JWT validation using a public key from a URL
- In-memory caching
- Header-based decorator (`@require_jwt_auth`)
- AWS Lambda and FastAPI-ready
- Configurable via environment or programmatic init

## Usage

```python
from sso_auth import jwt_auth_required,inject_jwt_user
from sso_auth.config import init_sso_config
from sso_auth.exceptions import JWTValidationError
from sso_auth.validators import check_authorization

init_sso_config(
    sso_public_key_url=SSO_PUBLIC_KEY_URL,
    sso_issuer=SSO_ISSUER
)
or 
: export then env with SSO_PUBLIC_KEY_URL and SSO_ISSUER

@jwt_auth_required
def my_func(header, *args,**kwargs):
# header 
    user = header.get("user", {})
    ...

# calling 
test(headers,body)


or 
try:
    user = check_authorization(token)
except JWTValidationError as e:
    ...
```

```python

@inject_jwt_user
def lambda_handler(event, context):
    """inject_jwt_user with inject the decoded payload into user  of requestContext 
    if authentication fails then  inject_jwt_user returns with statusCode 401 """
    user = event['requestContext']['user']