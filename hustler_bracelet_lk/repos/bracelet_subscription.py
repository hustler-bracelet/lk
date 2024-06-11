from .generic import Repository
from hustler_bracelet_lk.database.models import BraceletSubscription
from hustler_bracelet_lk.database.engine import DATABASE_SESSION

bracelet_subscription_repository = Repository(
    model=BraceletSubscription,
    session=DATABASE_SESSION
)
