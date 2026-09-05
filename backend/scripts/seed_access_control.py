from app.bootstrap import seed_access_control
from app.core.database import SessionLocal


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_access_control(db)
    print("Access-control seed completed.")
