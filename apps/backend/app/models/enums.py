from enum import StrEnum


class ApplicationStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    screening = "screening"
    reviewed = "reviewed"


class AssetKind(StrEnum):
    profile_image = "profile_image"
    intro_video = "intro_video"
    portfolio = "portfolio"


class ScreeningStatus(StrEnum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
