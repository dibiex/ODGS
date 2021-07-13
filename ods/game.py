from ods.config import ssh, ssh_key
from mcstatus import MinecraftServer


class Game():

    def __init__(self, config, ip_address):
        self.config = config
        self.ip_address = ip_address
    
    def install():
        pass

    def game_start():
        pass

    def game_stop():
        pass

class Minecraft(Game):

    def check_game_start():
        running=False
        timeout=300
        server = MinecraftServer.lookup('%s:%s' % (ip,'25565'))
        while not running:
            try:
                print('Check if minecraft started')
                server.status()
                running=True
            except:                
                if timeout == 0:
                    print(e)
                    raise Exception("Timeout, server didn't start")
                else:
                    print('Waiting for server to start')
                    time.sleep(30)
                    timeout -= 30


    def game_start(self):
        ssh.connect(hostname=ip_address, username=self.config.SSH_USERNAME, pkey=ssh_key)
        stdin, stdout, stderr = ssh.exec_command('screen -d -m -S Minecraft')
        stdin, stdout, stderr = ssh.exec_command("screen -r Minecraft -X stuff $'cd /srv/minecraft && java -Xmx1024M -Xms1024M -jar spigot-1.16.1.jar nogui\n'")
        ssh.close()

        self.check_game_start()
