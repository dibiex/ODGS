import os
import paramiko

from dotenv import load_dotenv

load_dotenv()

class Config():

    TOKEN = os.getenv('TOKEN')
    
    INSTANCE_REGION = 'fra1'
    INSTANCE_TYPE = 's-1vcpu-1gb'
    INSTANCE_NAME = 'test'

    FIRSTRUN_IMAGE = 'ubuntu-16-04-x64'
    FIRSTRUN = True
    
    SSH_TIMEOUT = 120
    SSH_KEY_NAME = 'minecraft_key'
    SSH_USERNAME = 'root'

    GAME_NAME = os.getenv('GAME_NAME')
    GAME_PORT = os.getenv('GAME_PORT')
    

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

key_path = os.getenv('SSH_KEY')
ssh_key = paramiko.RSAKey.from_private_key_file(key_path)
