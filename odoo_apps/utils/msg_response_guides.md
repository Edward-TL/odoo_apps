# HTTP STATUS:
    200: ok
    201: Created
    404: Not found
    406: Not Acceptable
    
# MESSAGE ERRORS:
## 10XX : Main App Errors
    '1000': 'App Server Error, please contact the admin' # Global Error
    '1001': 'Missing Headers'
    '1002': 'Missing Parameters'
    '1003': 'Invalid offset or limit'
    '1004': 'Invalid Locale'
    '1005': 'Invalid Timezone'
    '1006': 'You exceeded the limit of requests per minute, Please try again after sometime.'
## 11XX : Http Errors
    '1101': 'Unauthorized'
    '1102': 'Not authorized to access'
    '1103': 'Unprocessable Entity'
    '1104': 'Authentication Failed'
    '1105': 'Not Found'

## 12XX : Auth Erorrs
    '1201': 'Your session is expired, please login again' # Token expired
    '1202': 'Your sessions is invalid' # JWT verification error
    '1203': 'Your sessions is invalid' # Error encountered while decoding JWT token
    '1204': 'Your sessions token is invalid' # Invalid token
    '1205': 'You are Unauthorized, Please login' # You are Unauthorized, Please login
    '1206': 'Authentication Error, User Not found' # Authentication Error, User Not found

## 13XX Session Errors
    '1301': 'Invalid Credentials'
    '1302': 'Invalid Login Type'
    '1303': 'Invalid Social Type'
    '1304': 'Login Error'
    '1305': 'You Account is disabled by the admin.'
    '1306': 'Invalid mobile number.'
    '1307': 'Wrong confirmation code! Try again.'
    '1308': 'Invalid email or password'
    '1309': 'Your account already exist in the app, please try to login.'
    '1310': 'Your request is invalid or your request time is over, please try again.'
    '1311': 'You are not authorized to access this app'
    '1312': 'An issue in the Active Directory Service, please contat the Administrator'
    '1313': 'your email still not confirmed, please confirm your email'
    '1314': 'Email link has been expired'
    '1315': 'Your account is not activated Please verify your email to activate the account'
    '1316': 'You cannot delete user until his requests been completed or cancelled'
    '1317': 'This number has already registered'
    '1318': 'Please before you login with google account first sign up'
    '1319': 'Your old mobile number is wrong'
    '1320': 'confirmation code is expired! Try again'
    '1321': 'You cannot delete provider until he completed or cancelled his requests'
    '1322': 'Your account was blocked by Admin. Please contact admin at support@laancare.com'

data_found:             'Data found'
  no_data_found:          'No data found'
  not_found:              'Not found'
  x_not_found:            '%{name} not found!'
  update_successfully:    'Updated successfully'
  x_update_successfully:  '%{name} updated successfully'
  created_successfully:   'Created successfully'
  x_created_successfully: '%{name} created successfully'
  deleted_successfully:   'Deleted successfully'
  x_deleted_successfully: '%{name} deleted successfully'
  request_submitted:      'Order %{code} Code has been Submitted successfully'
  orders_not_found:       'No orders yet'