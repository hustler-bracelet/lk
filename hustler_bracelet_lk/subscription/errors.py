class UserAlreadySubscribedError(BaseException):
    pass


class UserNotSubscribedError(BaseException):
    pass


class TransactionNotApprovedError(BaseException):
    pass


class UserAlreadyAddedError(BaseException):
    pass


class UserAlreadyRemovedError(BaseException):
    pass


class UnmigratedSubscriptionError(BaseException):
    pass
