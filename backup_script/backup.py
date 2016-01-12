#What can't be bought can't be stolen...
#...No men in suits, no means of exchange
#as the message spreads through highway of information
#translated from the lyrics of Kuolleiden runoilijoiden seura by Abuktio

import paramiko, ConfigParser, os, base64, datetime
from Crypto.Cipher import AES

def fTransfer(loc, rem):
    #write log
    logfile.write(datetime.datetime.now().strftime("%H:%M:%S")+' '+ loc+' -> '+rem+'\n')

    #transfer file through SFTP
    sftp.put(loc, rem)


#Fetch crypted information
cryptfile = open('/home/feideri/.config/backup/credentials','r')
parser = ConfigParser.ConfigParser()
parser.readfp(cryptfile)

user = parser.get('crypted_info', 'username')
pwd = parser.get('crypted_info', 'pwd')
cryptfile.close()


#Fetch key for decryption
keyfile = open('/etc/backup/key','r')
key = keyfile.readline()
keyfile.close()


#Decryption
cipher = AES.new(key,AES.MODE_ECB)
deUser = cipher.decrypt(base64.b64decode(user))
dePass = cipher.decrypt(base64.b64decode(pwd))


#strip whitespaces
deUser = deUser.strip()
dePass = dePass.strip()


#Fetch filepaths
pathfile = open('/home/feideri/.config/backup/paths','r')
pathArray = []

for line in pathfile:
    pathArray.append(os.path.normpath(line.rstrip('\n')))

pathfile.close()


#SSH connection
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('lakka.kapsi.fi',username=deUser, password=dePass)


#SFTP for file transfer
sftp = client.open_sftp()


#create log file
logfile = open('/home/feideri/.config/backup/logs/'+datetime.datetime.now().strftime("%Y-%m-%d")+'.log','w')


for item in pathArray:

    #variable check for root directory
    isRootDir = 1
    
    for dirName, subdirList, fileList in os.walk(item):

        if isRootDir == 1:
            dirName = dirName.split(os.path.sep)[-1]
            rootDir = '/siilot/8/feideri/'+dirName
            isRootDir = 0
            lpath = item+'/'
            rpath = rootDir+'/'

            #write log
            logfile.write(datetime.datetime.now().strftime("%H:%M:%S")+' '+item+' -> '+rootDir+'\n')
            
            try:
                sftp.mkdir(rootDir, mode=0777) #make a new directory if it doesn't exist
            except IOError, e:
                pass

        else:
            dirName = dirName.replace(item, "")
            subDir = rootDir+dirName
            lpath = item+dirName+'/'
            rpath = subDir+'/'

            #write log
            logfile.write(datetime.datetime.now().strftime("%H:%M:%S")+' '+item+dirName+' -> '+subDir+'\n')
            
            try:
                sftp.mkdir(subDir, mode=0777) #make a new directory if it doesn't exist
            except IOError, e:
                pass

            
        #Loop through files in the directory
        for fname in fileList:
            local = lpath+fname
            remote = rpath+fname

            try:
                localinfo = os.stat(local)
                remoteinfo = sftp.stat(remote)

                if localinfo.st_size != remoteinfo.st_size:
                    fTransfer(local, remote) #file transfer if filesize differs
                
            except IOError, e:
                fTransfer(local, remote) #file transfer if file doesn't exist

logfile.close()                
sftp.close()

client.close()
