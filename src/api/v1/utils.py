from starlette import status

from src.api.deps import TokenDep
from src.auth import UserRole
from src.model.errors import ErrorCode, ServiceError


def verify_admin_role(token_claims: TokenDep) -> None:
    """
    Check if the user has the 'admin' role in the token claims.
    If not, raise a ServiceError with a 403 status code.
    """

    if UserRole.admin not in token_claims.roles:
        raise ServiceError(
            status_code=status.HTTP_403_FORBIDDEN,
            message="You do not have permission to access this resource",
            code=ErrorCode.invalid_request,
        )
