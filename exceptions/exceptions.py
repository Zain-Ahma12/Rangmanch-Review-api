from fastapi.responses import JSONResponse
from fastapi import Request, status

class InvalidPlayNameError(Exception):
    """
    Exception raised when no data is found for a given play name.
    
    This exception is intended to be caught by a FastAPI exception handler and converted into an appropriate HTTP response.
    
    Attributes:
        play_name: The play name for which no data was found.
    """
    def __init__(self, play_name: str) -> None:
        self.play_name = play_name

class InvalidReviewIdError(Exception):
    """
    Exception raised when no data is found for a given review id.
    
    This exception is intended to be caught by a FastAPI exception handler and converted into an appropriate HTTP response.
    
    Attributes:
        id: The review id for which no data was found.
    """
    def __init__(self, id: int) -> None:
        self.id = id


# Custom handlers
async def invalid_play_name_handler(request: Request, exc: InvalidPlayNameError) -> JSONResponse:
    """
    Handle :class:`InvalidPlayNameError` exceptions.
    
    Returns an HTTP 404 response containing an error code, a descriptive message, and the play name that could not be found.
    
    Args:
        request: The incoming FastAPI request.
        exc: The ``InvalidPlayNameError`` exception that was raised.
    
    Returns:
        A ``JSONResponse`` with HTTP 404 status and details about the missing play name.
    """
    return JSONResponse(
        status_code = 404,
        content = {
            "error": "play_name_not_found",
            "message": f"No data for play name: {exc.play_name}",
            "play_name": exc.play_name
        }
    )
    

async def invalid_review_id_handler(request: Request, exc: InvalidReviewIdError) -> JSONResponse:
    """
    Handle :class:`InvalidReviewIdError` exceptions.
    
    Returns an HTTP 404 response containing an error code, a descriptive message, and the review id that could not be found.
    
    Args:
        request: The incoming FastAPI request.
        exc: The ``InvalidReviewIdError`` exception that was raised.
    
    Returns:
        A ``JSONResponse`` with HTTP 404 status and details about the missing review id.
    """
    return JSONResponse(
        status_code = 404,
        content = {
            "error": "review_id_not_found",
            "message": f"No data for review id: {exc.id}",
            "id": exc.id
        }
    )