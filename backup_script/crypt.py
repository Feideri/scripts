from Crypto.Cipher import AES
import base64

user = 'user'.rjust(32)
pwd = 'pass'.rjust(32)

key = 'B2C798CBD937892A263DD16B64E68D8D'

cipher = AES.new(key,AES.MODE_ECB)

encoded = base64.b64encode(cipher.encrypt(user))
encoded2 = base64.b64encode(cipher.encrypt(pwd))
# ...
decoded = cipher.decrypt(base64.b64decode(encoded))
print encoded
print encoded2
print decoded

