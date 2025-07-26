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
    """Represents a bot user."""
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
        """Converts the user object to a dictionary for database operations."""
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
        """Creates a User object from a dictionary."""
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
    """Represents user preferences for job matching."""
    user_id: int
    language_preference: LanguagePreference = LanguagePreference.BOTH
    location_preference: LocationPreference = LocationPreference.BOTH
    preferred_country: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    notification_frequency: int = 1  # 0=on-demand, 1=once, 2=twice, 3=three times
    notification_times: List[time] = field(default_factory=lambda: [time(9, 0)])
    onboarding_completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the preferences object to a dictionary for database operations."""
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
        """Creates a UserPreferences object from a dictionary."""
        # Parse notification times
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
    """Represents a job listing."""
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
        """Converts the job object to a dictionary for database operations."""
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
        """Creates a Job object from a dictionary."""
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
class JobNotification:
    """Represents a job notification sent to a user."""
    user_id: int
    job_id: int
    notification_type: NotificationType = NotificationType.DAILY
    is_clicked: bool = False
    sent_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the notification object to a dictionary for database operations."""
        return {
            'user_id': self.user_id,
            'job_id': self.job_id,
            'notification_type': self.notification_type.value,
            'is_clicked': self.is_clicked,
            'sent_at': self.sent_at,
            'clicked_at': self.clicked_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobNotification':
        """Creates a JobNotification object from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            job_id=data['job_id'],
            notification_type=NotificationType(data.get('notification_type', 'daily')),
            is_clicked=data.get('is_clicked', False),
            sent_at=data.get('sent_at'),
            clicked_at=data.get('clicked_at')
        )

@dataclass
class JobOpinion:
    """Represents community opinion about a job or company."""
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

    def to_dict(self) -> Dict[str, Any]:
        """Converts the opinion object to a dictionary for database operations."""
        return {
            'job_id': self.job_id,
            'company': self.company,
            'source': self.source,
            'opinion_text': self.opinion_text,
            'sentiment': self.sentiment.value,
            'author': self.author,
            'source_url': self.source_url,
            'scraped_at': self.scraped_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobOpinion':
        """Creates a JobOpinion object from a dictionary."""
        return cls(
            id=data.get('id'),
            job_id=data['job_id'],
            company=data['company'],
            source=data['source'],
            opinion_text=data['opinion_text'],
            sentiment=Sentiment(data.get('sentiment', 'neutral')),
            author=data.get('author'),
            source_url=data.get('source_url'),
            scraped_at=data.get('scraped_at'),
            created_at=data.get('created_at')
        )

@dataclass
class SearchLog:
    """Represents a search log entry."""
    user_id: int
    search_type: str
    search_parameters: Dict[str, Any]
    results_count: int = 0
    executed_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the search log object to a dictionary for database operations."""
        return {
            'user_id': self.user_id,
            'search_type': self.search_type,
            'search_parameters': self.search_parameters,
            'results_count': self.results_count,
            'executed_at': self.executed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchLog':
        """Creates a SearchLog object from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            search_type=data['search_type'],
            search_parameters=data.get('search_parameters', {}),
            results_count=data.get('results_count', 0),
            executed_at=data.get('executed_at')
        )

@dataclass
class BotStatistics:
    """Represents daily bot statistics."""
    date: datetime
    total_users: int = 0
    active_users: int = 0
    jobs_scraped: int = 0
    notifications_sent: int = 0
    search_requests: int = 0
    created_at: Optional[datetime] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the statistics object to a dictionary for database operations."""
        return {
            'date': self.date.date() if isinstance(self.date, datetime) else self.date,
            'total_users': self.total_users,
            'active_users': self.active_users,
            'jobs_scraped': self.jobs_scraped,
            'notifications_sent': self.notifications_sent,
            'search_requests': self.search_requests
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotStatistics':
        """Creates a BotStatistics object from a dictionary."""
        return cls(
            id=data.get('id'),
            date=data['date'],
            total_users=data.get('total_users', 0),
            active_users=data.get('active_users', 0),
            jobs_scraped=data.get('jobs_scraped', 0),
            notifications_sent=data.get('notifications_sent', 0),
            search_requests=data.get('search_requests', 0),
            created_at=data.get('created_at')
        )

@dataclass
class JobMatch:
    """Represents a job match result for a user."""
    job_id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    apply_url: str
    match_score: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobMatch':
        """Creates a JobMatch object from a dictionary."""
        return cls(
            job_id=data['job_id'],
            title=data['title'],
            company=data.get('company'),
            location=data.get('location'),
            apply_url=data['apply_url'],
            match_score=data.get('match_score', 0)
        )

@dataclass
class UserStats:
    """Represents user statistics."""
    total_notifications: int
    jobs_clicked: int
    last_notification: Optional[datetime]
    registration_date: Optional[datetime]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStats':
        """Creates a UserStats object from a dictionary."""
        return cls(
            total_notifications=data.get('total_notifications', 0),
            jobs_clicked=data.get('jobs_clicked', 0),
            last_notification=data.get('last_notification'),
            registration_date=data.get('registration_date')
        )

