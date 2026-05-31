"""Import all ORM models so SQLAlchemy can resolve relationships."""

from app.models.user import Users  # noqa: F401
from app.models.customer import Customers  # noqa: F401
from app.models.merchant import Merchants, Channels  # noqa: F401
from app.models.transaction import TransactionLive  # noqa: F401
from app.models.scoring import RuleHit, AuditLog  # noqa: F401
from app.models.case import ReviewCase  # noqa: F401
from app.models.loan import Loans  # noqa: F401
from app.models.analyst import ModelConfig  # noqa: F401
from app.models.card_velocity import CardVelocityStats  # noqa: F401
