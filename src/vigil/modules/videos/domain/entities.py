from ....shared.base import Entity

from .value_objects import VideoId, VideoStatus

class Video(Entity):

	def __init__(self, id: VideoId, status: VideoStatus):
		self.id: VideoId = id
		self.statu: VideoStatus = status