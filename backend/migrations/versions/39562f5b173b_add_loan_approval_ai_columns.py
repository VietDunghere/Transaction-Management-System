"""add_loan_approval_ai_columns

Revision ID: 39562f5b173b
Revises: 6949263b39c8
Create Date: 2026-04-17 09:51:15.620704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39562f5b173b'
down_revision: Union[str, Sequence[str], None] = '6949263b39c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI feature columns matching train_loan_model.py v4 feature contract."""
    # AI input features (snapshot at application time)
    op.add_column('loans', sa.Column('person_age', sa.Integer(), nullable=True))
    op.add_column('loans', sa.Column('person_income', sa.Numeric(precision=18, scale=2), nullable=True))
    op.add_column('loans', sa.Column('person_home_ownership', sa.String(length=20), nullable=True))
    op.add_column('loans', sa.Column('person_emp_length', sa.Integer(), nullable=True))
    op.add_column('loans', sa.Column('loan_grade', sa.String(length=2), nullable=True))
    op.add_column('loans', sa.Column('loan_intent', sa.String(length=30), nullable=True))
    op.add_column('loans', sa.Column('cb_person_default_on_file', sa.String(length=1), nullable=True))
    op.add_column('loans', sa.Column('cb_person_cred_hist_length', sa.Integer(), nullable=True))
    # AI output
    op.add_column('loans', sa.Column('pd_score', sa.Numeric(precision=6, scale=4), nullable=True))
    op.add_column('loans', sa.Column('risk_level', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Remove AI columns."""
    op.drop_column('loans', 'risk_level')
    op.drop_column('loans', 'pd_score')
    op.drop_column('loans', 'cb_person_cred_hist_length')
    op.drop_column('loans', 'cb_person_default_on_file')
    op.drop_column('loans', 'loan_intent')
    op.drop_column('loans', 'loan_grade')
    op.drop_column('loans', 'person_emp_length')
    op.drop_column('loans', 'person_home_ownership')
    op.drop_column('loans', 'person_income')
    op.drop_column('loans', 'person_age')
