from .generic import Repository
from hustler_bracelet_lk.database.models import BraceletTransaction
from hustler_bracelet_lk.database.engine import DATABASE_SESSION

bracelet_transaction_repository = Repository(
    model=BraceletTransaction,
    session=DATABASE_SESSION
)
