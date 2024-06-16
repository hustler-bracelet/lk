
from sqlalchemy import select

from .generic import Repository

from sqlalchemy.ext.asyncio import AsyncSession

from hustler_bracelet_lk.database.models import BraceletSubscription


def get_bracelet_subscription_repository(session) -> 'SubscriptionRepo':
    return SubscriptionRepo(BraceletSubscription, session)


class SubscriptionRepo(Repository[BraceletSubscription]):
    async def get_last_subscription(self, telegram_id: int) -> BraceletSubscription | None:
        query = (
            select(BraceletSubscription)
            .where(
                BraceletSubscription.telegram_id == telegram_id,
            )
            .order_by(
                BraceletSubscription.will_end_on.desc(),
            )
            .limit(1)
        )

        return (await self._session.execute(query)).scalar()
