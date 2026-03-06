
import json
import jwt
from more_sso.cache import Cache
from more_sso.config import get_sso_config,get_pem
from more_sso.exceptions import JWTValidationError
from jwt import PyJWTError
from functools import partial
_public_key_cache = Cache(ttl_seconds=60*60)

def get_public_key() -> str:
    cached_key = _public_key_cache.get('PUBLIC_KEY')
    if cached_key:
        return cached_key,_public_key_cache.get('AUDIENCE') , _public_key_cache.get("REDIS")

    cfg = get_sso_config()
    public_key = get_pem(cfg['public_key_uri'])
    _public_key_cache.set('PUBLIC_KEY', public_key)
    _public_key_cache.set('AUDIENCE', cfg.get('audience'))  
    _public_key_cache.set("REDIS",cfg.get("REDIS"))
    return public_key,cfg.get('audience'),cfg.get("REDIS")

def validate_jwt(token: str, options: dict = {},live_session=False) -> dict:
    public_key,audience,REDIS = get_public_key()
    decode_fn = jwt.decode
    if audience and options.get("verify_aud", True):
         decode_fn = partial(jwt.decode,audience=audience)
    try:
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1].strip()
        payload = decode_fn(
            token,
            token_type='access',
            key=public_key,
            algorithms=["RS256"],
            options=options
        )

        if live_session and not REDIS:
            raise Exception('redis not configured for live session ')
        if live_session and options.get("verify_aud", True):
            prev_session = REDIS.get(f"{payload['aud']}:{payload['user_id']}")
            if prev_session != payload['session_id']:
                raise JWTValidationError(f"session expired or User  has loggedin in other device ")

        return payload
    except PyJWTError as e:
        raise JWTValidationError(f"JWT validation failed: {str(e)}")

def validate_token(token, options:dict={},live_session=False) -> dict:
    user = validate_jwt(token, options,live_session=live_session)
    return user