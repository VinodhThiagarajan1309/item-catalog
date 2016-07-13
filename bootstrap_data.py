from sqlalchemy import create_engine , select, delete 
from sqlalchemy.orm import sessionmaker
 
from database_setup import Base, User, Category, Item
 
engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



#Menu for UrbanBurger
# user1 = User(name = "Vinodh" , email = "vinodh.thiagarajan@gmail.com", picture="Hello.jpeg")

# session.add(user1)
# session.commit()

# item1 = Item(title = "This is title 1", description=" Description for title 1",user_id=2,category_id=1)
# item2 = Item(title = "This is title 2", description=" Description for title 2",user_id=3,category_id=2)
# item3 = Item(title = "This is title 3", description=" Description for title 3",user_id=2,category_id=3)
# item4 = Item(title = "This is title 4", description=" Description for title 4",user_id=3,category_id=3)
# item5 = Item(title = "This is title 5", description=" Description for title 5",user_id=2,category_id=4)

# session.add(item1)
# session.add(item2)
# session.add(item3)
# session.add(item4)
# session.add(item5)

# session.commit()

categories = select([Category])
cur_categories = session.execute(categories)
master=[]
dict_master = {}
for category in session.query(Category):
	print category.serialize
	dict_cat = {}
	dict_cat["id"] = category.id
	dict_cat["name"] = category.name
	items = session.query(Item).filter_by(category_id=category.id)
	cur_item = session.execute(items).fetchall()
	lst_items_for_this_cat = []
	for item in session.query(Item).filter_by(category_id=category.id):
		print item.serialize
		
		lst_items_for_this_cat.append(item.serialize)
	dict_cat["items"] = lst_items_for_this_cat
	master.append(category.serialize)
dict_master["Category"] = master
print dict_master
# s = (session.query(Category.id , Category.name , Item.category_id ,  Item.description , Item.id,Item.title  )
#     .outerjoin(Item, Category.id == Item.category_id))
# #s = select([Item])
# result = session.execute(s)
# d = {}
# for row in result:
# 	#stmt = User.delete().where(User.id == row.id)
# 	d[row[0]] = row
# print(d)