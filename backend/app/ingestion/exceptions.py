class ElexonAPIError(Exception):
    """Base class for Elexon ingestion failures."""


class ElexonHTTPError(ElexonAPIError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"Elexon API returned HTTP {status_code}: {message}")
        self.status_code = status_code


class ElexonTimeoutError(ElexonAPIError):
    pass


class ElexonRateLimitedError(ElexonHTTPError):
    pass
