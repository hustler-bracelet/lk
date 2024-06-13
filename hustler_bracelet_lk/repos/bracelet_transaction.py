from .generic import Repository
from hustler_bracelet_lk.database.models import BraceletTransaction


def get_bracelet_transaction_repository(session) -> Repository[BraceletTransaction]:
    return Repository(BraceletTransaction, session)
