import io
import pytest
from fastapi import status

from vigil.modules.users.domain.value_objects import UserId
from vigil.modules.videos.application.exceptions import FilenameNoneOrEmptyError, SizeUnknownError, InvalidFileError

UPLOAD_URL = "/videos/upload/"
GET_ALL_URL = "/videos/"
GET_URL = "/videos/"


class TestUpload:
    async def test_upload_success(self, client_with_video_service, video):
        mock_service, client = client_with_video_service
        mock_service.upload_video.return_value = video

        fake_file = io.BytesIO(b"fake video content")
        response = await client.post(
            UPLOAD_URL,
            files={
                "file": (
                    video.filename.value,
                    fake_file,
                    "video/mp4"
                )
            }
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["filename"] == video.filename.value
        assert data["size_bytes"] == video.size_bytes.value
        assert data["status"] == str(video.status)

    async def test_upload_returns_correct_schema(self, client_with_video_service, video):
        mock_service, client = client_with_video_service
        mock_service.upload_video.return_value = video
        fake_file = io.BytesIO(b"fake video content")
        response = await client.post(
            UPLOAD_URL,
            files={
                "file": (
                    video.filename.value,
                    fake_file,
                    "video/mp4"
                )
            }
        )

        data = response.json()
        assert set(data.keys()) == {"filename", "size_bytes", "status", "id"}

    @pytest.mark.parametrize("filename, file", [
        (None, io.BytesIO(b"fake video content")),
        ("", io.BytesIO(b"fake video content")),
    ])
    async def test_upload_fails(self, client_with_video_service, video, filename, file):
        mock_service, client = client_with_video_service
        mock_service.upload_video.return_value = video

        response = await client.post(
            UPLOAD_URL,
            files={
                "file": (
                    filename,
                    file,
                    "video/avi"
                )
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetAll:
    async def test_get_all_success(self, client_with_video_service, video, mock_current_user):
        mock_service, client = client_with_video_service
        mock_service.list_by_owner.return_value = [video]

        response = await client.get(
            GET_ALL_URL
        )

        videos = response.json()

        assert len(videos) >= 1
        found_video = next((v for v in videos if v["id"] == str(video.id.value)))
        assert found_video is not None
        assert found_video["filename"] == video.filename.value
        assert found_video["size_bytes"] == video.size_bytes.value
        assert found_video["status"] == str(video.status)

class TestGet:
    async def test_get_success(self, client_with_video_service, video):
        mock_service, client = client_with_video_service
        mock_service.get_by_id.return_value = video

        response = await client.get(
            f"{GET_URL}{str(video.id.value)}",
        )

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["filename"] == video.filename.value
        assert data["size_bytes"] == video.size_bytes.value
        assert data["status"] == str(video.status)