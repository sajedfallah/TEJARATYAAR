from app.core.security import create_access_token, decode_access_token


def test_access_token_roundtrip():
    token = create_access_token("user-123", ["manager"])
    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"
    assert payload["roles"] == ["manager"]
    assert payload["exp"] > payload["iat"]
