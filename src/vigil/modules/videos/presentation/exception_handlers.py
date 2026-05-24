from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..domain.exceptions import FileEmptyError, WrongFileExtensionError, InvalidFileError, FileAlreadyExists, FileTooLargeError, FileTooSmallError, FileNotFound
from ..application.exceptions import FileAccessDeniedError, FilenameNoneOrEmptyError, SizeUnknownError


def register_exception_handlers(app: FastAPI) -> None:

    # --- Invalid file ---

	@app.exception_handler(FilenameNoneOrEmptyError)
	async def filename_none_or_empty_handler(request: Request, exc: FilenameNoneOrEmptyError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "Filename is missing"}
		)
	
	@app.exception_handler(SizeUnknownError)
	async def size_unknown_handler(request: Request, exc: SizeUnknownError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "File size is unknown"}
		)
	
	@app.exception_handler(FileAccessDeniedError)
	async def file_access_denied_handler(request: Request, exc: FileAccessDeniedError):
		return JSONResponse(
			status_code=status.HTTP_403_FORBIDDEN,
			content={"detail" : "Access to file is denied"}
		)
	
	@app.exception_handler(FileEmptyError)
	async def file_empty_handler(request: Request, exc: FileEmptyError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "File is empty"}
		)
	
	@app.exception_handler(FileTooSmallError)
	async def file_too_small_handler(request: Request, exc: FileTooSmallError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "File is too small"}
		)

	@app.exception_handler(FileTooLargeError)
	async def file_too_large_handler(request: Request, exc: FileTooLargeError):
		return JSONResponse(
			status_code=status.HTTP_413_CONTENT_TOO_LARGE,
			content={"detail" : "File is too large"}
		)
	
	@app.exception_handler(WrongFileExtensionError)
	async def wrong_file_extension_handler(request: Request, exc: WrongFileExtensionError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "File has wrong extension. Allowed extensions: .mp4, .avi, .mov"}
		)

	@app.exception_handler(InvalidFileError)
	async def invalid_file_handler(request: Request, exc: InvalidFileError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			content={"detail" : "File is invalid"}
		)
	
	@app.exception_handler(FileNotFound)
	async def file_not_found_handler(request: Request, exc: FileNotFound):
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"detail" : "File not found"}
		)
	
	@app.exception_handler(FileAlreadyExists)
	async def file_already_exists_handler(request: Request, exc: FileAlreadyExists):
		return JSONResponse(
			status_code=status.HTTP_400_BAD_REQUEST,
			content={"detail" : "File already exists"}
		)