from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, Budget, Expense
from app.schemas.schemas import BudgetCreate, BudgetUpdate, BudgetOut

router = APIRouter()

def build_budget_response(budget: Budget, db: Session) -> BudgetOut:
    total_spent = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == budget.user_id,
        Expense.category == budget.category,
        Expense.date.like(f"{budget.month}%")
    ).scalar() or 0.0

    percent = (total_spent / budget.amount_allocated * 100) if budget.amount_allocated > 0 else 0.0
    status_str = "normal"
    if percent >= 100:
        status_str = "exceeded"
    elif percent >= 80:
        status_str = "warning"

    return BudgetOut(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        amount_allocated=budget.amount_allocated,
        month=budget.month,
        amount_spent=round(total_spent, 2),
        utilization_percentage=round(percent, 1),
        status=status_str,
        created_at=budget.created_at
    )

@router.get("/", response_model=List[BudgetOut])
def get_budgets(
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_month = month or datetime.utcnow().strftime("%Y-%m")
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == current_month
    ).all()

    return [build_budget_response(b, db) for b in budgets]

@router.post("/", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == budget_in.category,
        Budget.month == budget_in.month
    ).first()

    if existing:
        existing.amount_allocated = budget_in.amount_allocated
        db.commit()
        db.refresh(existing)
        return build_budget_response(existing, db)

    budget = Budget(
        user_id=current_user.id,
        category=budget_in.category,
        amount_allocated=budget_in.amount_allocated,
        month=budget_in.month
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return build_budget_response(budget, db)

@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if budget_in.amount_allocated is not None:
        budget.amount_allocated = budget_in.amount_allocated

    db.commit()
    db.refresh(budget)
    return build_budget_response(budget, db)

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(budget)
    db.commit()
    return None
