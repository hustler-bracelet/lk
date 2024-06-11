from enum import Enum


class FinanceTransactionType(str, Enum):
    INCOME = 'INCOME'
    SPENDING = 'SPENDING'


class CompletionStatus(str, Enum):
    PENDING = 'PENDING'
    VERIFIED = 'VERIFIED'
    REJECTED = 'REJECTED'


class TransactionType(str, Enum):
    INCOME = 'INCOME'
    OUTCOME = 'OUTCOME'


class TransactionStatus(str, Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    DECLINED = 'DECLINED'


# TODO: объединить FinanceTransactionType и TransactionType;
#       объединить TransactionStatus и CompletionStatus
