from hustler_bracelet_lk.database.models import User
from hustler_bracelet_lk.repos.user import user_repository


class ReferralService:
    def __init__(self, user: User):
        self._user = user

    async def get_referred_users(self) -> list[User]:
        users = await user_repository.filter()
        return [user for user in users if user.referred_by == self._user.telegram_id]
        # TODO HACK: костыль!

    async def get_referral_link(self) -> str:
        return f'https://t.me/hustler_bracelet_lk?start={self._user.telegram_id}'
