from django.shortcuts import render
 
from SerialNumberGenerator.baseFunction import *

from SerialNumberGenerator.models import *

class CreditManagement(View):
    def post(self,request):
        response={"message":"","status":"failed","code":200,"callBack":"CreditManaagement"}
        try:
            headers = getHeaders(request)
            response.update({"message":"X-CSRF-TOKEN is missing in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='':
                response.update({"message":"points are missing"})
                if 'points' in request.POST and request.POST['points']!="":
                    response.update({"message":"remarks is missing"})
                    if "remarks" in request.POST and request.POST['remarks']!='':
                        response=self.createCreditManagementDef(headers['X_CSRF_TOKEN'],request.POST['points'],request.POST['remarks'],response)
        except Exception as e:
            response.update({"message":str(e),"status": "failed"})
        return HttpResponse(dumps(response))
    def createCreditManagementDef(self,userToken,points,remarks,response):
        usersCheck=verifyUserToken1(userToken)
        response.update({"message":'Invalid User'})
        if usersCheck:
            userId=usersCheck['userId']
            statusCheck=loads(dumps(db.users.find({"userId":userId},{"_id":0,"userStatus":1,'userId':1})))
            userId1=statusCheck[0]['userId']
            print(userId1)
            status=statusCheck[0]['userStatus']
            print(status)
            response.update({"message":"valid user"})
            if status=="active":
                db.points.insert({"pointsReqested":points,"requestId":requestId(),"userId":userId1,"paymentModeOn":timeStamp(),"paymentMode":"","isPaymentDone":"No"})
        response.update({"message":"points are requested","code":200,"status":"success","callBack":"CreditManagment"})
        return response

#**********************************************************************#
class LoadCredit(View):
    def post(self,request):
        response={"message":"","status":"failed","code":200,"callBack":"LoadCredit"}
        try:
            headers = getHeaders(request)
            response.update({"message":"X-CSRF-TOKEN is missing in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='':
                usersCheck=verifyUserToken(headers['X_CSRF_TOKEN'])
                print(usersCheck)
                roleName=usersCheck['role']
                print(roleName)
                userId=usersCheck['userId']
                if roleName=="admin":
                    #response.update({"message":"Enter points"})
                    response=self.loadCreditDef(headers['X_CSRF_TOKEN'],userId,request.POST.get("points",None),response)
                
        except Exception as e:
            response.update({"message":str(e),"status":"failed"})
        return HttpResponse(dumps(response),content_type="application/json")

    def loadCreditDef(self,userToken,userId,points,response):
        points=loads(dumps(db.points.find({"userId":userId},{"_id":0,"pointsReqested":1})))
        print(points)
    
        response.update({"message":"Request Sent Successfully","pointsData":points[0]['pointsReqested'],"status":"success","code":200})
        if points:
            credit=points[0]['pointsReqested']
            adminValid=loads(dumps(db.users.find({"userId":userId,"role":"admin"},{"role":1})))
            credit1=loads(dumps(db.credits.find({"userId":userId},{"balance":1})))
            balance=credit1[0]['balance']
            print("(((((((((((((((((())))))))))))))))))",balance)
            role=adminValid[0]['role']
            response.update({"message":""})
            if adminValid:
                db.credits.update({"userId":userId},{"$set":{"balance":int(balance)+int(credit),"added":int(credit),"addedBy":role,"userId":userId}})
                response.update({"message":"Successfully credit the request","status":"success","code":200})

        return response

'''
class History(View):
    def post(self,request):
        response={"message":"","status":"failed","code":200,"callBack":"History"}
        try:
            headers = getHeaders(request)
            response.update({"message":"X-CSRF-TOKEN is missing in headers"})
            if 'X_CSRF_TOKEN' in  headers and headers['X_CSRF_TOKEN']!='':
                usersCheck=verifyUserToken(headers['X_CSRF_TOKEN'])
                response.update({"message":"userId are missing"})
                if 'userId' in request.POST and request.POST['userId']!="":
                    response.update({'message': 'action Type is required and must credit,debit'})
                    if 'action' in request.POST and request.POST['action']!='':
                        response=hisDef(request.POST['userId'],request.POST['action'],response)            
        except Exception as e:
            response.update({"message":str(e),"status":"failed"})
        return HttpResponse(dumps(response),content_type="application/json")

def hisDef(userId,action,response):
    credit=loads(dumps(db.credits.find({"userId":userId},{"_id":0,"userId":1})))
    userId=credit[0]['userId']
    print(userId)
    users=loads(dumps(db.users.find({'userId':userId},{'userName':1,"_id":0,'userId':1})))
    userName=users[0]['userName']
    userId1=users[0]['userId']
    db.history.insert({'userId':userId1,'userName':userName,'reason':"",'time':timeStamp(),'action':action})
    response.update({'message':'Fetched Successfully','code':200,'status':'success'})
    return response
'''
