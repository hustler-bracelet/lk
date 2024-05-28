from enum import Enum


class FinanceTransactionType(str, Enum):
    INCOME = 'income'
    SPENDING = 'spending'


class CompletionStatus(str, Enum):
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'


class PayoutReason(str, Enum):
    REFERRAL = 'referral'
    ACTIVITY = 'activity'
    OTHER = 'other'


class PaymentReason(str, Enum):
    BRACELET = 'bracelet'
    OTHER = 'other'
