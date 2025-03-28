from fastapi import APIRouter


router = APIRouter(prefix="/v1")


@router.get("")
def get_v1_root() -> dict[str, str]:
    return {}


# router.include_router(product.router)
