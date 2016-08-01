from flask import (
    Flask, render_template, request, redirect, jsonify, url_for, flash)
from sqlalchemy import create_engine, asc, select, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import string
from collections import OrderedDict

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Ajax call placed from javascript
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user '+'is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    try:
        user = session.query(User).filter_by(
            email=login_session['email']).one()
    except NoResultFound:
        user = User(
            name=login_session['username'],
            email=login_session['email'],
            picture=login_session['picture'])
        session.add(user)
        flash(
            '%s, welcome to Item Catalog Application.' %
            login_session['username'])
        session.commit()
    flash("You are now logged in as %s" % login_session['username'])
    return 'success'


# Logout call endpoint
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You are now logged out.")
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.' +
                login_session['access_token'], 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view All Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    lst_category = []
    for category in session.query(Category):
        dict_serialized_category = category.serialize
        lst_items_for_this_cat = []
        for item in session.query(Item).filter_by(category_id=category.id):
            lst_items_for_this_cat.append(item.serialize)
        if(len(lst_items_for_this_cat) > 0):
            dict_serialized_category["Item"] = lst_items_for_this_cat
        lst_category.append(dict_serialized_category)
    return jsonify(Category=lst_category)


# JSON end point to view the detailed item information
@app.route('/catalog/<string:item_name>/JSON')
def itemJSON(item_name):
    print item_name
    item_detail = session.query(Item).filter_by(title=item_name).one()
    return jsonify(Item_Detail=item_detail.serialize)


# Show all Items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item).order_by(desc(Item.id))
    picture = ''
    if 'picture' in login_session:
        picture = login_session['picture']
    else:
        picture = None
    return render_template(
        'showCatalog.html',
        categories=categories,
        latestItems=latestItems,
        picture=picture,
        STATE=state)


# Create New Category
@app.route('/catalog/newcategory', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        inputCategoryName = request.form['inputCategoryName']
        try:
            checkIfCategoryExists = session.query(Category).filter_by(
                name=inputCategoryName).one()
            if(checkIfCategoryExists and
                    checkIfCategoryExists.name == inputCategoryName):
                flash(
                    'Category named %s already exists.' +
                    'Please create a category with different name.' %
                    inputCategoryName)
                return render_template('newCategory.html', warnedFlash=True)
        except NoResultFound, e:
            newCategory = Category(name=inputCategoryName)
            session.add(newCategory)
            flash('New Category %s Successfully Created' % newCategory.name)
            session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')


# Display items for the given category
@app.route('/catalog/<string:category_name>/items/')
def showCategoryItems(category_name):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    picture = ''
    if 'picture' in login_session:
        picture = login_session['picture']
    else:
        picture = None

    categories = session.query(Category).order_by(asc(Category.name))
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        categoryItems = session.query(Item).filter_by(
            category_id=category.id).order_by(desc(Item.title))
        return render_template(
            'showCategoryItems.html',
            categories=categories,
            categoryItems=categoryItems,
            STATE=state,
            picture=picture)
    except NoResultFound, e:
        flash(
            'No category named %s  exists.' +
            'Please look for a valid category.' % category_name)
        return render_template(
            'showCategoryItems.html',
            categories=categories,
            warnedFlash=True,
            STATE=state,
            picture=picture)


# Show detailed item view
@app.route('/catalog/<string:item_name>')
def showCategoryItemDetailed(item_name):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    try:
        picture = ''
        if 'picture' in login_session:
            picture = login_session['picture']
        else:
            picture = None
        itemDetail = session.query(Item).filter_by(title=item_name).one()
        isItemOwner = False
        if 'email' in login_session:
            if itemDetail.user.email == login_session['email']:
                isItemOwner = True
        return render_template(
            'showCategoryItemDetailed.html',
            itemDetail=itemDetail,
            picture=picture,
            isItemOwner=isItemOwner,
            STATE=state)
    except NoResultFound, e:
        return render_template(
            'showCategoryItemDetailed.html',
            picture=picture)


# Create a new item
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).order_by(asc(Category.name))
    picture = ''
    if 'picture' in login_session:
        picture = login_session['picture']
    else:
        picture = None

    if 'username' not in login_session:
        flash('Kindly login to create an item.')
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        inputItemName = request.form['itemTitle']
        try:
            checkIfItemTitleExists = session.query(Item).filter_by(
                title=inputItemName).one()
            if(checkIfItemTitleExists and
                    checkIfItemTitleExists.title == inputItemName):
                flash(
                    'Item name %s already exists. Please create an' +
                    'item with different name.' % inputItemName)
                return render_template(
                    'newItem.html',
                    categories=categories,
                    picture=picture,
                    warnedFlash=True)
        except NoResultFound:
            users = session.query(User).filter_by(email=login_session['email'])
            user = users[0]
            newItem = Item(
                title=request.form['itemTitle'],
                description=request.form['itemDesc'],
                category_id=request.form['selectedCategoryId'],
                user_id=user.id)
            session.add(newItem)
            session.commit()
            flash('New Item %s Successfully Created' % (newItem.title))
            return redirect(
                url_for('showCategoryItemDetailed', item_name=newItem.title))
    else:
        return render_template(
            'newItem.html', categories=categories,
            picture=picture, STATE=state)


# Edit given item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    picture = ''
    if 'picture' in login_session:
        picture = login_session['picture']
    else:
        picture = None
    item = session.query(Item).filter_by(title=item_name).one()
    if 'username' not in login_session:
        flash('Kindly login to update an item.')
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if item.user.email == login_session['email']:
            item.title = request.form['itemTitle']
            item.description = request.form['itemDesc']
            item.category_id = request.form['selectedCategoryId']
            session.add(item)
            session.commit()
            flash('Item Successfully Updated.')
            return redirect(
                url_for('showCategoryItemDetailed', item_name=item.title))
        else:
            flash('You are not authorized to update this item.')
            return redirect(
                url_for('showCategoryItemDetailed', item_name=item.title))
    else:
        isItemOwner = False
        if item.user.email == login_session['email']:
            isItemOwner = True
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template(
                'editItem.html', categories=categories, item=item,
                isItemOwner=isItemOwner, picture=picture)
        else:
            flash('You are not authorized to update this item.')
            return redirect(
                url_for('showCategoryItemDetailed', item_name=item.title))


# Delete Given Item
@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(item_name):
    if request.method == 'POST':
        try:
            itemToDelete = session.query(
                Item).filter_by(id=request.form['itemId']).one()
            if 'username' not in login_session:
                flash('Kindly login to delete an item.')
            elif itemToDelete.user.email == login_session['email']:
                session.delete(itemToDelete)
                flash('%s successfully deleted.' % item_name)
                session.commit()
                return redirect(url_for('showCatalog'))
        except NoResultFound:
            flash('No such item exists.')
            return redirect(url_for('showCatalog'))


# Developer Util Methods
@app.route('/deleteAllUsers')
def handydeleteUsers():
    itemToDelete = session.query(User)
    for item in itemToDelete:
        session.delete(item)
        session.commit()
    return 'Deleted All Users'


@app.route('/deleteAllCategories')
def handydeleteCat():
    itemToDelete = session.query(Category)
    for item in itemToDelete:
        session.delete(item)
        session.commit()
    return 'Deleted All Categories'


@app.route('/deleteAllItems')
def handydeleteItems():
    itemToDelete = session.query(Item)
    for item in itemToDelete:
        session.delete(item)
        session.commit()
    return 'Deleted All Items'


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=10000)
