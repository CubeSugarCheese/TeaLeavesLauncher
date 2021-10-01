class AuthError(Exception):
    pass


class RefreshTokenError(AuthError):
    def __str__(self):
        return "RefreshToken is invalid"
