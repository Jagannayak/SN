from SerialNumberGenerator.baseFunction import *
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from SerialNumberGenerator.models import *

# Create your views here.
#testing#797897809780
#**********************************Login******************************************#
class Login(View):
    def get(self,request):
        try:
            response={"message":"GET Method Not Allowed","status":"failed","code":405,"callBack":"Login"}
        except Exception as e:
            response.update({"message":str(e)})	
        return HttpResponse(dumps(response))	
    def post(self,request):
        response={"message":"","status":"failed","code":400,"callBack":"Login"}
        try:
            response.update({"message":"Please enter name"})
            if 'name' in request.POST and  request.POST['name']!='':
                response.update({"message":"Please enter password"})
                if 'password' in request.POST and request.POST['password']!='':
                    response= loginDef(request.POST['name'],request.POST['password'],response)
        except Exception as e:
            response.update({"message":str(e),"status":"failed"})
        return HttpResponse(dumps(response),content_type="application/json")

def loginDef(userName,password,response) :
    try:
        usersCheck = loads(dumps(db.users.find_one({"userName": userName, 'password': password}, {"_id":0}))) # check the users in db
        response.update({"message":'Invalid Login Credentials'}) # return the message if user not available
        if usersCheck is not None: # checking the users
            response.update({"message":"User is Inactive"})
            if usersCheck['userStatus'] == 'active':
                userId = usersCheck['userId']
                userName = usersCheck['userName']
                response.update({
                    'message': 'User Already Signed-in', 'status': 'success', 'code': 200, 'userName': userName, 
                    'userToken': usersCheck['userToken'], 
                    })
                if not usersCheck['userToken']: 
                    userToken = generateUserToken()
                    db.users.update({"userName":userName},{'$set':{'userToken': userToken}}) # generate token when login
                    response.update({"message":'Login Successful', 'userToken':userToken,"code":200,"status":"success"})
                
                    # logFiles(userId,response['callBack'],userName,timeStamp(),'POST',response['message'],response)
    except Exception as e: response.update({"message":str(e),"status":"failed"})
    return response       

#******************************LogOut**************************************#
class LogOut(View):
    def get(self,request):
        try:
            response={"message":"GET Method Not Allowed","status":"failed","code":405,"callBack":"LogOut"}
        except Exception as e:
            response.update({"message":str(e)})	
        return HttpResponse(dumps(response))	
    def post(self,request):
        response={"message":"","status":"failed","code":400,"callBack":"Roles"}
        try:
            headers = getHeaders(request)
            response.update({"message":"please pass X-CSRF-TOKEN in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='': 
                response= logoutDef(headers['X_CSRF_TOKEN'],response)
        except Exception as e:
            response.update({"message":str(e),"status": "failed"})
        return HttpResponse(dumps(response),content_type="application/json")
def logoutDef(userToken,response):
    usersCheck=loads(dumps(db.users.find({"userToken":userToken},{'_id':0,'userName':1})))
    response.update({"message":'Invalid User'})
    if usersCheck:
        userName=usersCheck[0]['userName']
        db.users.update({"userName":userName},{"$set":{'userToken':""}})           
        response.update({"message":' LogOut Successfully','status':'success','code':200})   
    return response


#*******************************CreateUsers*************************************#
class UserActions(View):
    def get(self,request):
        response={"message":"GET Method Not Allowed","status":"failed","code":405,"callBack":"UserCreation"}	
        return HttpResponse(dumps(response))
    def post(self,request):
        response={"message":"","status":"failed","code":400,"callBack":"UserCreation"}
        try:
            headers = getHeaders(request)
            response.update({"message":"please pass X-CSRF-TOKEN in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='': 
                response.update({"message":"userName is missing and must be 3-20 characters"})
                if 'userName' in  request.POST and re.match('^[a-z A-Z 0-9]{3,20}$',request.POST['userName']):
                    response.update({"message":"mailId is missing"})
                    if 'mailId' in  request.POST and request.POST['mailId']!='':
                        response.update({"message":"password must contain 8-12  characters with atleast one lower case, one upper case, special character and numeric"})
                        if 'password' in  request.POST and passwordValidator(request.POST['password']) is True:
                            response.update({"message":"contactNumber must be 10-14 digits"})
                            if 'contactNumber' in request.POST and re.match('^[0-9]{10,14}$',request.POST['contactNumber']):
                                response=self.usersDef(request.POST['userName'],request.POST['mailId'],request.POST['password'],request.POST['contactNumber'],response)
        except Exception as e:
            response.update({"message":str(e),"status": "failed"})
        return HttpResponse(dumps(response),content_type="application/json")

    def usersDef(self,userName,mailId,password,contactNumber,response):
        userId=generateUserId() #generate the unique userId
        userInfo=loads(dumps(db.users.find({"userName":userName})))#find the userName in users collection
        response.update({"message":"User Already Existed"})
        if not userInfo: #checking userinfo ,if data not  exist then insert into the users collection
            db.users.insert({"userName":userName,"password":password,"role":'user',"userId":userId,"userToken":"","createdOn":timeStamp(),"createdBy":userId,'userStatus':'active','phoneNumber':contactNumber,'email':mailId,})
            response.update({"message":"Created Successfully","status":"success","code":200}) # return success message
        return response
    
    def delete(self,request):
        response={"message":"","status":"failed","code":400,"callBack":"UserAction"}
        try:
            headers = getHeaders(request)
            response.update({"message":"please pass X-CSRF-TOKEN in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='':
                response.update({'message':'userId is missing'})
                if 'userId' in request.GET and request.GET['userId']!='':
                    response=self.deleteDef(request.GET['userId'],response)
        except Exception as e:
            response.update({"message":str(e),"status": "failed"})
        return HttpResponse(dumps(response),content_type="application/json")

    def deleteDef(self,userId,response):
        try:
            userInfo=loads(dumps(db.users.find({"userId":userId},{'_id':0})))
            response.update({"message":'Invalid userId'})
            if userInfo[0]['userStatus']=='active':
                db.users.update({'userId':userId},{'$set':{'userStatus':'inactive'}})
                response.update({"message":"updated to inactive","status":"success","code":200}) # return success message
            else:
                response.update({'message':"already inactive","status":"success","code":200})
        except Exception as e: response.update({"message":str(e),"status":"failed"})
        return response

#****************************************************

class GetUsers(View):
    def get(self,request):
        response={"message":"","status":"failed","code":400,"callBack":"GetUsers"}
        try:
            headers = getHeaders(request)
            response.update({"message":"please pass X-CSRF-TOKEN in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='': 
                response = getUsersDef(headers['X_CSRF_TOKEN'],response)
        except Exception as e:

            response.update({"message":str(e),"status": "failed"})
        return HttpResponse(dumps(response),content_type="application/json")
def getUsersDef(token,response):
    userRoleCheck = verifyUserToken1(token)
    userId=userRoleCheck['userId']
    if userRoleCheck:
        if userRoleCheck['role']=='admin':
            usersData=loads(dumps(db.users.find({},{"_id":0,'createdOn':0,'createdBy':0})))
            response.update({"message":"Fetched Successfully","UsersData":usersData,"status":"success","code":200})
            print("SSSSSSSSS",usersData)
            #print(usersData)
            response.update({"message":"Fetched Successfully","UsersData":usersData,"status":"success","code":200})
        elif userRoleCheck['role']=='user':
            usersData=loads(dumps(db.users.find({'userId':userId},{"_id":0,'createdOn':0,'createdBy':0})))
            response.update({"message":"Fetched Successfully","UsersData":usersData,"status":"success","code":200})
    return response       
