from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_catlog import Categories, Base, Items, User

engine = create_engine('sqlite:///categories_item.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Menu for main Categories
catogry1 = Categories(name="Soccer")

session.add(catogry1)
session.commit()

catogry2 = Categories(name="Basketball")

session.add(catogry2)
session.commit()

catogry3 = Categories(name="Baseball")

session.add(catogry3)
session.commit()

catogry4 = Categories(name="Frisbee")

session.add(catogry4)
session.commit()

catogry5 = Categories(name="Snowboarding")

session.add(catogry5)
session.commit()

catogry6 = Categories(name="Rock Climbing")

session.add(catogry6)
session.commit()

catogry7 = Categories(name="Foosball")

session.add(catogry7)
session.commit()

catogry8 = Categories(name="Skating")

session.add(catogry8)
session.commit()

catogry9 = Categories(name="Hockey")

session.add(catogry9)
session.commit()

print" Adedd Menu for Categories"
