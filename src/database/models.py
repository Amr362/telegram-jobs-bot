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

@dataclass
class JobNotification:
    user_id: int
    job_id: int
    notification_type: NotificationType = NotificationType.DAILY
    is_clicked: bool = False
    sent_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class JobOpinion:
    job_id: int
    company: str
    source: str
    opinion_text: str
    sentiment: Sentiment = Sentiment.NEUTRAL
    author: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class SearchLog:
    user_id: int
    search_type: str
    search_parameters: Dict[str, Any]
    results_count: int = 0
    executed_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class BotStatistics:
    date: datetime
    total_users: int = 0
    active_users: int = 0
    jobs_scraped: int = 0
    notifications_sent: int = 0
    search_requests: int = 0
    created_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class JobMatch:
    job_id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    apply_url: str
    match_score: int

@dataclass
class UserStats:
    total_notifications: int
    jobs_clicked: int
    last_notification: Optional[datetime]
    registration_date: Optional[datetime]

