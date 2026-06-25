from app.core.security import (
    create_access_token,
    create_refresh_token
)

print(
    create_access_token(
        {"sub": "1"}
    )
)

print(
    create_refresh_token(
        {"sub": "1"}
    )
)