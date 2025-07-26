from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from enum import Enum

class LanguagePreference(Enum):
    ARABIC = "arabic"
    GLOBAL = "global"
    BOTH = "both"

class LocationPreference(Enum):
    SPECIFIC = "specific"
    REMOTE = "remote"
    BOTH = "both"

class JobType(Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    REMOTE = "remote"
    FREELANCE = "freelance"

class LinkStatus(Enum):
    WORKING = "working"
    BROKEN = "broken"
    UNKNOWN = "unknown"

class NotificationType(Enum):
    DAILY = "daily"
    MANUAL = "manual"
    URGENT = "urgent"

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class User:
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language_code': self.language_code,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            telegram_id=data['telegram_id'],
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            language_code=data.get('language_code'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class UserPreferences:
    user_id: int
    language_preference: LanguagePreference = LanguagePreference.BOTH
    location_preference: LocationPreference = LocationPreference.BOTH
    preferred_country: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    notification_frequency: int = 1
    notification_times: List[time] = field(default_factory=lambda: [time(9, 0)])
    onboarding_completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'language_preference': self.language_preference.value,
            'location_preference': self.location_preference.value,
            'preferred_country': self.preferred_country,
            'skills': self.skills,
            'notification_frequency': self.notification_frequency,
            'notification_times': [t.strftime('%H:%M') for t in self.notification_times],
            'onboarding_completed': self.onboarding_completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        notification_times = []
        if data.get('notification_times'):
            for time_str in data['notification_times']:
                if isinstance(time_str, str):
                    hour, minute = map(int, time_str.split(':'))
                    notification_times.append(time(hour, minute))
                elif isinstance(time_str, time):
                    notification_times.append(time_str)

        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            language_preference=LanguagePreference(data.get('language_preference', 'both')),
            location_preference=LocationPreference(data.get('location_preference', 'both')),
            preferred_country=data.get('preferred_country'),
            skills=data.get('skills', []),
            notification_frequency=data.get('notification_frequency', 1),
            notification_times=notification_times or [time(9, 0)],
            onboarding_completed=data.get('onboarding_completed', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Job:
    title: str
    apply_url: str
    source: str
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_range: Optional[str] = None
    source_job_id: Optional[str] = None
    skills_required: List[str] = field(default_factory=list)
    is_remote: bool = False
    is_active: bool = True
    link_status: LinkStatus = LinkStatus.UNKNOWN
    link_checked_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'location': self.location,
            'job_type': self.job_type.value if self.job_type else None,
            'salary_range': self.salary_range,
            'apply_url': self.apply_url,
            'source': self.source,
            'source_job_id': self.source_job_id,
            'skills_required': self.skills_required,
            'is_remote': self.is_remote,
            'is_active': self.is_active,
            'link_status': self.link_status.value,
            'link_checked_at': self.link_checked_at,
            'scraped_at': self.scraped_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        return cls(
            id=data.get('id'),
            title=data['title'],
            company=data.get('company'),
            description=data.get('description'),
            location=data.get('location'),
            job_type=JobType(data['job_type']) if data.get('job_type') else None,
            salary_range=data.get('salary_range'),
            apply_url=data['apply_url'],
            source=data['source'],
            source_job_id=data.get('source_job_id'),
            skills_required=data.get('skills_required', []),
            is_remote=data.get('is_remote', False),
            is_active=data.get('is_active', True),
            link_status=LinkStatus(data.get('link_status', 'unknown')),
            link_checked_at=data.get('link_checked_at'),
            scraped_at=data.get('scraped_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Notification:
    id: int
    user_id: int
    message: str
    sent_at: Optional[datetime] = None
    read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "sent_at": self.sent_at,
            "read": self.read
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            message=data.get("message", ""),
            sent_at=data.get("sent_at"),
            read=data.get("read", False),
        )


