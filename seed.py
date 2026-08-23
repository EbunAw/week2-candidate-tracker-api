from database import SessionLocal
from models import Candidate, Application


def seed_database():
    db = SessionLocal()

    try:
        candidate1 = Candidate(
            name="Ore George",
            email="ore.george@example.com",
            phone="08012345678"
        )

        candidate2 = Candidate(
            name="Jane Doe",
            email="jane@example.com",
            phone="08123456789"
        )

        db.add_all([candidate1, candidate2])
        db.commit()

        db.refresh(candidate1)
        db.refresh(candidate2)

        application1 = Application(
            candidate_id=candidate1.id,
            position="Python Developer",
            status="Applied"
        )

        application2 = Application(
            candidate_id=candidate1.id,
            position="Data Analyst",
            status="Interview"
        )

        application3 = Application(
            candidate_id=candidate2.id,
            position="Machine Learning Engineer",
            status="Applied"
        )

        db.add_all([application1, application2, application3])
        db.commit()

        print("Sample data seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()