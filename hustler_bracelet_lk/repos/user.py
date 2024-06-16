import pytz

from datetime import datetime
from sqlalchemy import select

from .generic import Repository
from hustler_bracelet_lk.database.models import User, BraceletSubscription


def get_user_repository(session) -> 'UserRepository':
    return UserRepository(session)


class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def get_all_referals_with_subscription(self, user_id: int) -> list[User]:
        query = (
            select(User)
            .where(
                User.referred_by == user_id,
                User.telegram_id.in_(
                    select(BraceletSubscription.telegram_id)
                    .where(
                        BraceletSubscription.will_end_on >= datetime.now(pytz.timezone('Europe/Moscow'))
                    )
                )
            )
        )

        return (await self._session.execute(query)).scalars().all()
