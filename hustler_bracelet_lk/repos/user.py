from .generic import Repository
from hustler_bracelet_lk.database.models import User


def get_user_repository(session) -> Repository[User]:
    return Repository(User, session)
