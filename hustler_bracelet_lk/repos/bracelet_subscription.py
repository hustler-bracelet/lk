from .generic import Repository

from sqlalchemy.ext.asyncio import AsyncSession

from hustler_bracelet_lk.database.models import BraceletSubscription


def get_bracelet_subscription_repository(session) -> Repository[BraceletSubscription]:
    return Repository(BraceletSubscription, session)
