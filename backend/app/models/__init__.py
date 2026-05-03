"""Import all ORM models so SQLAlchemy can resolve relationships."""

from app.models.user import User  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.merchant import Merchant, Channel  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.scoring import RuleHit, AuditLog  # noqa: F401
from app.models.case import ReviewCase  # noqa: F401
from app.models.loan import Loan  # noqa: F401
from app.models.analyst import ModelConfig  # noqa: F401
from app.models.card_velocity import CardVelocityStats  # noqa: F401
