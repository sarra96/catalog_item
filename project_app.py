from flask import Flask
from flask import render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from database_catlog import Base, User, Items, Categories
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import datetime
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
engine = create_engine('sqlite:///categories_item.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Login With google+
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')
    try: 
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)  
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

  
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

  
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

   
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output



def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT google+
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



# Home Page
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catogries = session.query(Categories).order_by(asc(Categories.name))
    items = session.query(Items).order_by(desc(Items.date)).limit(10)
    if 'username' not in login_session:
        return render_template('publicpage.html', catogries =catogries,items=items)
    else:
        return render_template('mycatalog.html', catogries =catogries,items=items)
         
# Specific  Cateogery
@app.route('/catalog/<string:catogry_name>/<int:catogry_id>/items/')
def specific_category(catogry_name,catogry_id):
    catogries = session.query(Categories).order_by(asc(Categories.name))
    items = session.query(Items).filter_by(category_id=catogry_id).all()
    item_count = session.query(Items).filter_by(category_id=catogry_id).count()
    if 'username' not in login_session:
        return render_template('public_catlog.html', catogries =catogries,items=items,count=item_count,catogry_name=catogry_name)
    else:
        return render_template('user_catlog.html', catogries =catogries,items=items,count=item_count,catogry_name=catogry_name)
   

# Specific  Items
@app.route('/catalog/catogery/<int:item_ctogrey>/item/<string:item_title>/')
def specific_item(item_ctogrey,item_title):
    item_description = session.query(Items).filter_by(title=item_title).one()

    if 'username' not in login_session:
        return render_template('public_item.html', content = item_description, title=item_title)
    else:
        return render_template('user_item.html', content = item_description, title=item_title,item_id=item_description.id )


########################################################################################

# Create a new Item
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def addItem():
    catogries = session.query(Categories).all()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            c = session.query(Categories).filter_by(name=request.form['category']).one()
            newItem = Items(title=request.form['name'], description=request.form['description'], category_id=c.id
                               ,user_id=login_session['user_id'],date=datetime.datetime.now())
            session.add(newItem)
            session.commit()
            return redirect(url_for('showCatalog'))
        else:
            return render_template('new_item.html',All =  catogries)
        
# Edit Item
@app.route('/catalog/<string:title_edit>/<int:Id_Edit>/edit', methods=['GET', 'POST'])
def editItem(title_edit,Id_Edit):
    
    if 'username' not in login_session:
        return redirect('/login')   
    itemEdit = session.query(Items).filter_by(id=Id_Edit).one()
    catogry = session.query(Categories).filter_by(id=itemEdit.category_id).one()
    catogries = session.query(Categories).all()
    if login_session['user_id'] != itemEdit.user_id:
        flash('You Can not Edit This Item As It Is Not Your Own Item ')
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        c_id = session.query(Categories).filter_by(name=request.form['category']).one()
        if request.form['name']:
            itemEdit.title = request.form['name']
        if request.form['description']:
            itemEdit.description = request.form['description']
        if request.form['category']:
            itemEdit.category_id = c_id.id
        session.add(itemEdit)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('edit_item.html',item=itemEdit,All=catogries,catogry_name=catogry.name)

# Delete Item
@app.route('/catalog/<string:title_delete>/<int:id_delete>/delete', methods=['GET', 'POST'])
def deleteItem(title_delete, id_delete):
    if 'username' not in login_session:
        return redirect('/login')
    itemDelete = session.query(Items).filter_by(id=id_delete).one()
    if login_session['user_id'] != itemDelete.user_id:
        flash('You Can not Delete This Item As It Is Not Your Own Item ')
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(itemDelete)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('delete_item.html', item=itemDelete)
#JSON APIs 
@app.route('/catalog/<int:cat_id>/items/JSON')
def ItemJSON(cat_id):
    items = session.query(Items).filter_by(category_id =cat_id).all()
    return jsonify(CatogryItem=[t.serialize for t in items])

@app.route('/catalog/categries/JSON')
def CatogryJSON():
    catogery = session.query(Categories).all()
    return jsonify(Catogries=[i.serialize for i in catogery])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
