""" Database Module - Supabase Integration

This module handles all database operations using Supabase.
"""

from .manager import SupabaseManager
from .models import User, Job, JobNotification, UserPreferences
from .queries import UserQueries, JobQueries, NotificationQueries

__all__ = [
    "SupabaseManager",
    "User",
    "Job",
    "Notification",
    "UserPreferences",
    "JobQueries",
    "NotificationQueries"
]

