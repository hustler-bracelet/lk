from .generic import Repository
from hustler_bracelet_lk.database.models import User
from hustler_bracelet_lk.database.engine import DATABASE_SESSION

user_repository = Repository(
    model=User,
    session=DATABASE_SESSION
)
