from database import engine, Base
import models  # noqa: F401 - ensures models are registered

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
