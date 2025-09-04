# decorators.py

from functools import wraps
from more_sso.validator import validate_jwt
from more_sso.exceptions import AccessDeniedError, JWTValidationError
from typing import TypeVar
import json
from more_sso.permissions import JSONPermission

RESPONSE_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":"*.more.in",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }

def json_response(status_code: int, detail: str="success", data: dict = {}):
    return {
        "statusCode": status_code,
        "headers":RESPONSE_HEADERS,
        "body": json.dumps({
            "detail": detail,
            "data": data or {}
        })
    }


def auth_required(permission_class=JSONPermission, permission: str = None, value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(event: dict , *args, **kwargs):
            token = event.get("headers", {}).get("Authorization", "") or  event.get("headers", {}).get("authorization", "")
            if not token:
                return json_response( 401, detail= "Unauthorized: Missing or invalid Authorization header")
            try:
                claims = validate_jwt(token)
                event['requestContext']['user'] = claims
                permission_obj = permission_class(claims, permission, value)

                if not permission_obj.has_access():
                    raise AccessDeniedError("Access denied: insufficient pervileges for this resource")
                
                return func(event, *args, **kwargs)
            except JWTValidationError as e:
                return json_response( 401, detail= str(e) )
        return wrapper
    
    return decorator

def root_auth_required(func):
    @wraps(func)
    def wrapper(event, context):
        token = event.get("headers", {}).get("Authorization", "") or  event.get("headers", {}).get("authorization", "")
        if not token :
            return json_response( 401, detail= "Unauthorized: Missing or invalid Authorization header")
        try:
            user = validate_jwt(token)
            event['requestContext']['user'] = user
            return func(event, context)
        except JWTValidationError as e:
            return json_response( 401, detail=str(e))
    return wrapper