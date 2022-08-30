import bcrypt
import dbAction
# Hash entered password
def hash_pw(password):
    # Convert password to array of bytes and generate the salt
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(14)

    # Hash the password with salt, return hashed pw for db manipulation
    hash = bcrypt.hashpw(pw_bytes, salt)
    return hash

# Check password with password in dictionary
def check_pw(entered_pw, db_pw): 
    # Encode entered password
    entered_pw.encode('utf-8')

    # Check password match and return result
    result = bcrypt.checkpw(entered_pw, db_pw)
    return result

def validate_login(user, pw):
    for account in dbAction.select_acc():
        if user.lower() == account[0].lower():
            if bcrypt.checkpw(pw.encode('utf-8'), account[1].encode('utf-8')):
                return True
    return False
    

