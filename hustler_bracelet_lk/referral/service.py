from hustler_bracelet_lk.database.models import User
from hustler_bracelet_lk.database.engine import SessionMaker
from hustler_bracelet_lk.repos.user import get_user_repository
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager


class ReferralService:
    def __init__(
            self,
            user: User,
            subscription_manager: SubscriptionManager,
            session,
    ):
        self._user = user
        self._subscription_manager = subscription_manager
        self._session = session

    async def get_referred_users(self) -> list[User]:
        user_repository = get_user_repository(self._session)
        all_referred_users = await user_repository.filter_by(
            referred_by=await self._user.awaitable_attrs.telegram_id
        )
        return [
            user for user in all_referred_users
            if await self._subscription_manager.get_user_subscription()
        ]

    async def get_referral_link(self) -> str:
        telegram_id = await self._user.awaitable_attrs.telegram_id
        return f'https://t.me/hustler_bracelet_lk?start={telegram_id}'
