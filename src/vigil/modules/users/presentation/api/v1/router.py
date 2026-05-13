from fastapi import APIRouter, Depends, Response, status

from ...dto.response import UserProfileSchema
from ...dto.request import UpdateUserSchema

from ......security.dependencies import get_current_user, CurrentUserDTO

from ....dependencies import UserService, get_user_service
from ....application.dto import UpdateUserDTO


router = APIRouter()


@router.get("/users/me/", tags=["user"])
async def get_me(
        current_user: CurrentUserDTO = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)) -> UserProfileSchema:
	user = await user_service.get_current_user_profile(current_user.id)

	return UserProfileSchema(
		email=user.email,
		username=user.username
	)


@router.patch("/users/me/", tags=["users"])
async def patch_me(
	update_user: UpdateUserSchema,
	current_user: CurrentUserDTO = Depends(get_current_user),
	user_service: UserService = Depends(get_user_service),
) -> Response:
	user = UpdateUserDTO(
		password=update_user.password,
		email=update_user.email,
		username=update_user.username,
		new_password=update_user.new_password
	)

	await user_service.update_current_user_profile(current_user.id, user)

	return Response(status_code=status.HTTP_200_OK)