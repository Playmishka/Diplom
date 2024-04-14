from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from DB import get_session
from models.modelsDB import product, main_storehouse, storehouse

router = APIRouter(prefix="/add_products")


@router.get("/main_storehouse")
def add_product_main_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    try:
        name_product = session.execute(select(product).where(product.c.id == product_id)).fetchone().name
        existing_entry = (session.execute(select(main_storehouse).where(main_storehouse.c.product == product_id))
                          .fetchone())
        if not existing_entry:
            session.execute(insert(main_storehouse).values(product=product_id, count=count))
            session.commit()
            return {"message": f"Product {name_product} added."}
        else:
            session.execute(update(main_storehouse).where(main_storehouse.c.product == product_id).values(
                count=main_storehouse.c.count + count
            ))
            session.commit()
            return {"message": f"Product {name_product} updated."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update main storehouse")


@router.get("/storehouse")
def add_product_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    try:
        name_product = session.execute(select(product).where(product.c.id == product_id)).fetchone().name
        existing_entry = (session.execute(select(main_storehouse).where(main_storehouse.c.product == product_id))
                          .fetchone())
        if not existing_entry:
            return {"message": f"Product {name_product} not found."}
        elif existing_entry.count < count:
            return {"message": f"Insufficient stock for Product {name_product}."}
        else:
            storehouse_entry = session.execute(select(storehouse).where(storehouse.c.product == product_id)).fetchone()
            if not storehouse_entry:
                session.execute(insert(storehouse).values(product=product_id, count=count))
            else:
                session.execute(update(storehouse).where(storehouse.c.product == product_id).values(
                    count=storehouse.c.count + count
                ))
            session.execute(update(main_storehouse).where(main_storehouse.c.product == product_id).values(
                count=main_storehouse.c.count - count
            ))
            session.commit()
            return {"message": f"Added {count} units of Product {name_product} to storehouse."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update storehouse")