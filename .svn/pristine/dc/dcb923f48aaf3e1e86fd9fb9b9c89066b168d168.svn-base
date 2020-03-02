from uuid import uuid4
from .settings import db
from datetime import datetime
from time import time, strftime
from bson.json_util import dumps, loads

# A basic fucntion for generating teh timestamp
def timeStamp(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Generate the unique userId for the customer.
def generateUserId():
    octaCharCode = list(str(uuid4()).replace('-', ''))[:-22]
    uniqueUserId = ''.join(octaCharCode)
    userIdExists = loads(dumps(db.users.find({"userId": uniqueUserId},{'_id':0}).count()))
    if userIdExists is not 0: generateUserId()
    else: return uniqueUserId

# Verify the Profile name existance.
def profileNameCheck(profileName, userId, result={}):
    profileName = loads(dumps(db.Profiles.find_one({'profileName': profileName, 'assignTo': userId}, {'_id': 0})))
    result.update({'message': 'Profile-Name Already Exists.'})
    if profileName is None: result.update({'message': 'pass'})
    return result

# Creates the Admin
def adminCreation():
    db.users.insert({
        'role': 'admin', 
        'password': 'Welcome@123',
        'createdOn': timeStamp(), 
        'createdBy': 'default-creation',
        'email': 'Accelsap@gmail.com',
        'phoneNumber': '9999999999',
        'userToken': '', 
        'userStatus': 'active',
        'userName': 'Administrator', 
        'userId': generateUserId()})
    return

# Validate the User Token and fetch the user data.
def verifyUserToken(userToken):
    user_data = loads(dumps(db.users.find_one({"userToken": userToken}, {'_id': 0, 'userToken': 0, 'password': 0, 'createdOn': 0, 'createdBy': 0}))) # check the token in db
    result = {'message': 'Un-authorized User.', 'status': 'failed'}
    if user_data is not None:
        result.update({'message': 'User is in-active.'})
        if user_data['userStatus'] == 'active':
            result.update({
                'message': 'user authorized', 'status': 'success', 'userId': user_data['userId'], 'userName': user_data['userName'], 
                'userStatus': user_data['userStatus'], 'role': user_data['role']
                })
    return result

# save the profile document
def save_profile_record(profile_document):
    profile_id = 'PROF-' + str(int(time())) + str(db.Profiles.count({}))
    profile_document.update({'profileId': profile_id})
    db.Profiles.insert_one(profile_document)
    return 

# Fetch profiles
def fetch_created_profiles(condition_set, result={}):
    profile_data = loads(dumps(db.Profiles.find(condition_set, {'_id': 0})))
    result.update({'message': 'Retrieved Successfully', 'code': 200, 'profiles': profile_data, 'status': 'success'})
    return result

# Delete the profiles
def delete_profile(condition_set, result={}):
    db.Profiles.remove(condition_set)
    result.update({'message': 'Removed Successfully', 'code': 200, 'status': 'success'})
    return result

# Verify the Profile name existance.
def check_profile(profileId, result={}):
    profileCheck = loads(dumps(db.Profiles.find_one({'profileId': profileId}, {'_id': 0})))
    result.update({'message': 'Profile Not Found.'})
    if profileCheck is not None: result.update({'message': 'pass'})
    return result