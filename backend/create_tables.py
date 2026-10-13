from app.db import engine, Base
from app import models #importing registers the table classes with base

Base.metadata.create_all(engine)
print("Tables created.")

