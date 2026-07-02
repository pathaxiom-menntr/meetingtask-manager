from fastapi import Query


class PaginationParams:
    """
    Reusable dependency for offset-based pagination.

    Usage in a router:
        @router.get("/")
        def list_items(pagination: PaginationParams = Depends()):
            return service.get_items(db, pagination.skip, pagination.limit)
    """

    def __init__(
        self,
        skip: int = Query(
            default=0,
            ge=0,
            description="Number of records to skip (offset)"
        ),
        limit: int = Query(
            default=20,
            ge=1,
            description="Max number of records to return"
        ),
    ):
        self.skip = skip
        self.limit = limit
