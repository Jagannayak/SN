from .baseFunction import *
from threading import Thread
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from .settings import OFFSET, LIMIT


def home(request):
    # Check for the admin collection, if not found insert a new one.
    if loads(dumps(db.users.find_one({'role': 'admin'}, {'_id': 0}))) is None:
        Thread(
            name='Admin Creation Thread',
            target=adminCreation,
            args=()
        ).start()
    return render(request, 'index.html')

class Profiles(View):

    def post(self, request):
        '''
        Date: 14/01/2020 
        Author: Mayur 
        Method: POST
        Headers: X-CSRF-TOKEN
        Parameters: name, description, length, type, exclusion_chars, prefix, isRandom
        Optional Parameters: assignTo, ratio, validity
        Description: Crates a profile for the generation of serial numbers.
        '''
        response = {'status': 'failed', 'code': 400, 'callback': 'Profiles'}
        try:
            serial_number_types = ['Alphanumeric_upper', 'Alphanumeric_lower', 'Numeric','Alphabetic_upper','Alphabetic_lower']
            headers = getHeaders(request)
            response.update({'message': 'X-CSRF-TOKEN is required.'})
            if 'X_CSRF_TOKEN' in headers and headers['X_CSRF_TOKEN'] != '':
                # Validate the user.
                token_result = verifyUserToken(headers['X_CSRF_TOKEN'])
                response.update({'message': token_result['message']})
                if token_result['status'] == 'success':
                    user_Id = token_result['userId']
                    user_name = token_result['userName']
                    user_role = token_result['role']
                    response.update({'message': 'name is required.'})
                    if 'name' in request.POST and request.POST['name'] != '':
                        response.update({'message': 'description is required.'})
                        if 'description' in request.POST and request.POST['description'] != '':
                            response.update({'message': 'length is required.'})
                            if 'length' in request.POST and request.POST['length'] != '':
                                response.update({'message': 'type is required which can be %s.' % serial_number_types})
                                if 'type' in request.POST and request.POST['type'] in serial_number_types:
                                    response.update({'message': 'exclusion_chars is required seperated by ",".'})
                                    if 'exclusion_chars' in request.POST and request.POST['exclusion_chars'] != '':
                                        response.update({'message': 'prefix is required.'})
                                        if 'prefix' in request.POST and request.POST['prefix'] != '':
                                            response.update({'message': 'isRandom can be true or false.'})
                                            if 'isRandom' in request.POST and request.POST['isRandom'] in ['true', 'false']:
                                                response.update(self.save_profile(
                                                    user_Id, user_name, user_role, request.POST['name'], request.POST['description'], request.POST['length'],
                                                    request.POST['type'], request.POST['exclusion_chars'],  request.POST['prefix'], request.POST.get('assignTo', user_Id),
                                                    request.POST.get('ratio', '1:1'), request.POST['isRandom'], request.POST.get('validity', 28), request, response
                                                    ))
        except Exception as error: response.update({'message': 'Internal Server Error.', 'error': str(error)})
        return HttpResponse(dumps(response, sort_keys=True), content_type='application/json')

    def save_profile(
        self, user_Id, user_name, user_role, profile_name, description, serial_number_length, serial_number_type, exclusion_characters, serial_number_prefix,
        assign_to, generation_ratio, is_random, expiry, request, response
        ):
        try:
            if user_role == 'admin': 
                # if the profile creator is admin ask him to whom he wants to assign the profile after creation.
                response.update({'message': 'assignTo is required.'})
                if 'assignTo' in request.POST and request.POST['assignTo'] != '':
                    assign_to =  request.POST['assignTo']

            # verify the profile name uniqueness
            check_profile = profileNameCheck(profile_name, user_Id, result=response)
            response.update({'message': check_profile['message']})
            if check_profile['message'] is 'pass':
                # Validating Rule for building the Serial Numbers size.
                length_check = self.__validateTheSerialNumberLength(serial_number_length, response)
                response.update({'message': length_check['message']})
                if length_check['message'] is 'ok':
                    # Validating Rule for building the Serial Numbers from exclusion characters.
                    exclsuion_check = self.__exclusionListCheck(exclusion_characters, serial_number_type, serial_number_length, response)
                    response.update({'message': exclsuion_check['message']})
                    if exclsuion_check['message'] is 'ok':
                        exclusionList = exclsuion_check['exclusionList']      
                        inclusionList = exclsuion_check['inclusionList']
                        response.pop('exclusionList'); response.pop('inclusionList')    
                        # Validating Rule for building the Serial Numbers from prefix characters.  
                        prefix_check = self.__validateSerialPrefix(serial_number_prefix, response)
                        response.update({'message': prefix_check['message']})
                        if prefix_check['message'] is 'ok':
                            # Since all the validations are passed save the profile.
                            profile_document = {
                                'prefix': serial_number_prefix,
                                'profileName': profile_name,
                                'description': description,
                                'length': serial_number_length,
                                'type': serial_number_type,
                                'exclusionList': exclusionList,
                                'assignTo': assign_to,
                                'ratio': generation_ratio,
                                'addedOn': timeStamp(),
                                'expiry': expiry,
                                'inclusionList':inclusionList,
                                'isRandom': is_random
                            }
                            save_profile_record(profile_document)
                            response.update({'message': 'Added Successfully', 'code': 200, 'status': 'success'})
        except Exception as error: response.update({'message': 'Internal Server Error.', 'error': str(error)}) 
        return response

    def __validateTheSerialNumberLength(self, size, response): 
        try: 
            serialNumberLength = int(size)
            response.update({'message': 'Serial number length must be at least 5-40 digits'})
            if  serialNumberLength in range (5, 41): response.update({'message': 'ok'})
        except ValueError: response.update({'message': 'Serial number length must be digits', 'error': 'value-error'})
        return response
   
    def __exclusionListCheck(self, exclusionChar, serialNumberSeries, serialNumberSize, response): 
        try:
            response.update({'message': 'excluded letter(s) are required seperated by (,)'})
            if ',' in exclusionChar:
                response.update({'message': 'excluded letters format error.'})
                exclusionList = exclusionChar.split(',')
                for exChar in exclusionList:
                     if len(exChar) not in [0, 1]: return response
                         
                # Exclusion Check for the Alphanumeric Upper pattern
                if serialNumberSeries == 'Alphanumeric_upper':
                    serailAlphaNumericUpperList = string.ascii_uppercase + string.digits
                    serailAlphaNumericUpperList = ','.join(serailAlphaNumericUpperList).split(',')
                    for sn_upper in exclusionList:
                        if sn_upper in serailAlphaNumericUpperList: 
                            serailAlphaNumericUpperList.pop(serailAlphaNumericUpperList.index(sn_upper))
                    if len(serailAlphaNumericUpperList) is 0: response.update({'message': 'no minimum characters to form the serial numbers'})
                    # elif len(serailAlphaNumericUpperList) < serialNumberSize: response.update({'message': 'no minimum characters to form the serial numbers'})
                    else: response.update({'message': 'ok', 'exclusionList':  exclusionList, 'inclusionList': serailAlphaNumericUpperList})

                # Exclusion Check for the Alphanumeric Lower pattern
                elif serialNumberSeries == 'Alphanumeric_lower':
                    serailAlphaNumericLowerList = string.ascii_lowercase + string.digits
                    serailAlphaNumericLowerList = ','.join(serailAlphaNumericLowerList).split(',')
                    for sn_lower in exclusionList:
                        if sn_lower in serailAlphaNumericLowerList: 
                            serailAlphaNumericLowerList.pop(serailAlphaNumericLowerList.index(sn_lower))
                    if len(serailAlphaNumericLowerList) is 0: response.update({'message': 'no minimum characters to form the serial numbers'})
                    # elif len(serailAlphaNumericLowerList) < serialNumberSize: response.update({'message': 'no minimum characters to form the serial numbers'})
                    else: response.update({'message': 'ok', 'exclusionList':  exclusionList,  'inclusionList': serailAlphaNumericLowerList})

                # Exclusion Check for the Numeric pattern
                elif serialNumberSeries == 'Numeric':
                    serialDigitsList = string.digits
                    serialDigitsList = ','.join(serialDigitsList).split(',')
                    for num in exclusionList:
                        if str(num) in serialDigitsList: serialDigitsList.pop(serialDigitsList.index(str(num)))
                    if len(serialDigitsList) is 0: response.update({'message': 'no minimum characters to form the serial numbers'})
                    # elif len(serialDigitsList) < serialNumberSize: response.update({'message': 'no minimum characters to form the serial numbers'})
                    else: response.update({'message': 'ok', 'exclusionList':  exclusionList, 'inclusionList': serialDigitsList })
                
                # Exclusion Check for the Alphabetic Upper pattern
                elif serialNumberSeries == 'Alphabetic_upper':
                    serailAlphabeticUpperList = string.ascii_uppercase
                    serailAlphabeticUpperList = ','.join(serailAlphabeticUpperList).split(',')
                    for sn_lower in exclusionList:
                        if sn_lower in serailAlphabeticUpperList: 
                            serailAlphabeticUpperList.pop(serailAlphabeticUpperList.index(sn_lower))
                    if len(serailAlphabeticUpperList) is 0: response.update({'message': 'no minimum characters to form the serial numbers'})
                    # elif len(serailAlphabeticUpperList) < serialNumberSize: response.update({'message': 'no minimum characters to form the serial numbers'})
                    else: response.update({'message': 'ok', 'exclusionList':  exclusionList,  'inclusionList': serailAlphabeticUpperList})
                
                # Exclusion Check for the Alphabetic Lower pattern
                elif serialNumberSeries == 'Alphabetic_lower':
                    serailAlphabeticLowerList = string.ascii_lowercase
                    serailAlphabeticLowerList = ','.join(serailAlphabeticLowerList).split(',')
                    for sn_lower in exclusionList:
                        if sn_lower in serailAlphabeticLowerList: 
                            serailAlphabeticLowerList.pop(serailAlphabeticLowerList.index(sn_lower))
                    if len(serailAlphabeticLowerList) is 0: response.update({'message': 'no minimum characters to form the serial numbers'})
                    # elif len(serailAlphabeticLowerList) < serialNumberSize: response.update({'message': 'no minimum characters to form the serial numbers'})
                    else: response.update({'message': 'ok', 'exclusionList':  exclusionList,  'inclusionList': serailAlphabeticLowerList})
        except Exception as e: response.update({'message': 'Internal Server Error', 'error': str(e)})
        return response

    def __validateSerialPrefix(self, prefix, response): 
        try: 
            response.update({'message': 'Serial number length must be at least 0-5 digits'})
            if len(prefix) not in range(0, 6): return response
            allowChars = string.ascii_lowercase + string.ascii_uppercase + string.digits
            for prefixChar in allowChars.split():
                if str(prefixChar) not in allowChars: 
                    response.update({'message':  str(prefixChar) + ' is not allowed in prefix'})
                    return response
            response.update({'message': 'ok'})
        except Exception as e: response.update({'message': 'Internal Server Error', 'error': str(e)})
        return response

    def get(self, request):
        '''
        Date: 14/01/2020 
        Author: Mayur 
        Method: GET
        Headers: X-CSRF-TOKEN
        Parameters: --
        Optional Parameters: profileUserId, offset, limit
        Description: Fetches the created profiles.
        '''       
        response = {'status': 'failed', 'code': 200, 'callback': 'Profiles'}
        try:
            headers = getHeaders(request)
            response.update({'message': 'X-CSRF-TOKEN is required.'})
            if 'X_CSRF_TOKEN' in headers and headers['X_CSRF_TOKEN'] != '':
                # Validate the user.
                token_result = verifyUserToken(headers['X_CSRF_TOKEN'])
                response.update({'message': token_result['message']})
                if token_result['status'] == 'success':
                    user_Id = token_result['userId']
                    user_name = token_result['userName']
                    user_role = token_result['role']
                    response.update(self.retrive_profile_data(
                        user_Id, user_name, user_role, response, request.GET.get('profileUserId', None), request.GET.get('offset', OFFSET), 
                        request.GET.get('limit', LIMIT))
                        ) 
        except Exception as e: response.update({'message': 'Internal Server Error', 'error': str(e)})
        return HttpResponse(dumps(response, sort_keys=True), content_type='application/json')
        
    def retrive_profile_data(self, user_Id, user_name, user_role, response, profile_userId, offset, limit):
        try:
            condition_set = {}
            if user_role is 'admin':
                response.update({'message': 'profileUserId is required'})
                if profile_userId is not None:
                    condition_set.update({'assignTo': profile_userId})
            else: condition_set.update({'assignTo': user_Id})
            response.update(fetch_created_profiles(condition_set, result=response))
        except KeyError as key_error: response.update({'message': key_error + ' key is referred before assignment.', 'error': 'KeyError'})
        except Exception as error: response.update({'message': 'Internal Server Error', 'error': str(error)})
        return response

    def delete(self, request):
        '''
        Date: 14/01/2020 
        Author: Mayur 
        Method: DELETE
        Headers: X-CSRF-TOKEN
        Parameters: profileId, 
        Optional Parameters: profileUserId
        Description: A service to delete the created profiles
        '''       
        response = {'status': 'failed', 'code': 200, 'callback': 'Profiles'}
        try:
            condition_set = {}
            headers = getHeaders(request)
            response.update({'message': 'X-CSRF-TOKEN is required.'})
            if 'X_CSRF_TOKEN' in headers and headers['X_CSRF_TOKEN'] != '':
                # Validate the user.
                token_result = verifyUserToken(headers['X_CSRF_TOKEN'])
                response.update({'message': token_result['message']})
                if token_result['status'] == 'success':
                    user_Id = token_result['userId']
                    user_name = token_result['userName']
                    user_role = token_result['role']
                    response.update({'message': 'profileId is required.'})
                    if 'profileId' in request.GET and request.GET['profileId'] != '':
                        if user_role is 'admin':
                            response.update({'message': 'profileUserId is required.'})
                            if 'profileUserId' in request.GET and request.GET['profileUserId'] != '': 
                                condition_set.update({
                                    'profileId':  request.GET['profileId'], 
                                    'assignTo': request.GET['profileUserId']
                                    })
                        else:
                            condition_set.update({'profileId':  request.GET['profileId']})
                        response.update(delete_profile(condition_set, result=response))
        except Exception as e: response.update({'message': 'Internal Server Error', 'error': str(e)})
        return HttpResponse(dumps(response, sort_keys=True), content_type='application/json')

    def put(self, request):
        '''
        Date: 14/01/2020 
        Author: Mayur 
        Method: PUT
        Headers: X-CSRF-TOKEN
        Parameters: name, description, length, type, exclusion_chars, prefix, isRandom
        Optional Parameters: assignTo, ratio, validity
        Description: Crates a profile for the generation of serial numbers.
        '''
        response = {'status': 'failed', 'code': 400, 'callback': 'Profiles'}
        try:
            serial_number_types = ['Alphanumeric_upper', 'Alphanumeric_lower', 'Numeric','Alphabetic_upper','Alphabetic_lower']
            
            headers = getHeaders(request)
            response.update({'message': 'X-CSRF-TOKEN is required.'})
            if 'X_CSRF_TOKEN' in headers and headers['X_CSRF_TOKEN'] != '':
                # Validate the user.
                token_result = verifyUserToken(headers['X_CSRF_TOKEN'])
                response.update({'message': token_result['message']})
                if token_result['status'] == 'success':
                    user_Id = token_result['userId']
                    user_name = token_result['userName']
                    user_role = token_result['role']
                    response.update({'message': 'profileId is required.'})
                    if 'profileId' in request.POST and request.POST['profileId'] != '':
                        response.update(check_profile(profileId, result=response))
                        if response['message'] is 'pass':
                            if user_role is 'admin': pass
                            else: 

                                response.update(self.save_profile(
                                    user_Id, user_name, user_role, request.POST['name'], request.POST['description'], request.POST['length'],
                                    request.POST['type'], request.POST['exclusion_chars'],  request.POST['prefix'], request.POST.get('assignTo', user_Id),
                                    request.POST.get('ratio', '1:1'), request.POST['isRandom'], request.POST.get('validity', 28), request, response
                                    ))
                    
        except KeyError as key_error: response.update({'message': key_error + ' key is referred before assignment.', 'error': 'KeyError'})
        except Exception as e: response.update({'message': 'Internal Server Error', 'error': str(e)})
        return HttpResponse(dumps(response, sort_keys=True), content_type='application/json')