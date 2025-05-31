from django.contrib.auth import get_user_model
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

User = get_user_model()

@dataclass
class OnlineUser:
    user_id: int
    last_seen: datetime

class OnlineUserTracker:
    _users = {}
    _lock = threading.Lock()
    TTL = timedelta(minutes=5)

    @classmethod
    def mark_online(cls, user_id: int):
        with cls._lock:
            cls._users[user_id] = OnlineUser(user_id=user_id, last_seen=datetime.utcnow())

    @classmethod
    def is_online(cls, user_id: int) -> bool:
        with cls._lock:
            user = cls._users.get(user_id)
            if user and datetime.utcnow() - user.last_seen < cls.TTL:
                return True
            else:
                cls._users.pop(user_id, None)
                return False

    @classmethod
    def get_all_online_users(cls) -> list[int]:
        now = datetime.utcnow()
        with cls._lock:
            expired = [uid for uid, user in cls._users.items() if now - user.last_seen >= cls.TTL]
            for uid in expired:
                del cls._users[uid]
            return list(cls._users.keys())

    @classmethod
    def get_online_user_count(cls):
        return len(cls.get_all_online_users())


class OnlineUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            OnlineUserTracker.mark_online(request.user.id)
        return response