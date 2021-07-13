import digitalocean
import paramiko
import time

from ods.config import ssh, ssh_key


class Provider():
    """
    Parent class for a provider
    """

    def __init__(self, config):
        self.config = config


    def wait_for_ssh(self, ip_address):
        """
        Test ssh connection multiple times until it connects
        or timeout passses
        """

        timeout = self.config.SSH_TIMEOUT
        connected = False
        while not connected:
            try:
                ssh.connect(hostname=ip_address, username=self.config.SSH_USERNAME, pkey=ssh_key)
                connected = True
                print("CONNECTED SSH")
                ssh.close()
            except Exception as e: 
                if timeout == 0:
                    print(e)
                    raise Exception("Timeout, can't connect to ssh")
                else:
                    print('Waiting for ssh')
                    time.sleep(5)
                    timeout -= 5


    def create_instance(self):
        """
        Creates a instance on the cloud provider.
        And waits for it to be available via ssh.
        """
        pass


    def end_instance(self):
        """
        Stops or destroys the instance depending on the provider.
        If it's destroyed it also creates a snapshot of the volume before. 
        """
        pass


    def erase(self):
        """
        Delete the instance/snapshot from the provider
        """
        pass

class DigitalOcean(Provider):

    def __get_latest_snapshot(self, manager):
        """
        Get the latest snapshot of the game
        """
        
        snapshots = manager.get_my_images()
        snapshots = [snap for snap in snapshots if snap.name.split('_')[0] == self.config.game_name]
        snap = min(snapshots, key=lambda x: int(x.name.split('_')[1]))
        return snap


    def __get_ssh_key(self, manager):
        
        keys = manager.get_all_sshkeys()
        key = [key for key in keys if key.name == self.config.SSH_KEY_NAME][0]
        return key


    def __wait_actions(self, actions):
        for action in actions:
            action.wait()


    def create_instance(self):
        
        manager = digitalocean.Manager(token=self.config.TOKEN)
        ssh_key = self.__get_ssh_key(manager)
        
        if not self.config.FIRSTRUN:
            image = self.__get_latest_snapshot(manager)
        else:
            image = self.config.FIRSTRUN_IMAGE

        droplet = digitalocean.Droplet(
            token=self.config.TOKEN,
            name=self.config.INSTANCE_NAME,
            region=self.config.INSTANCE_REGION,
            size_slug=self.config.INSTANCE_TYPE,
            image=image,
            backups=False,
            ssh_keys=[ssh_key]
        )
        
        droplet.create()
        self.__wait_actions(droplet.get_actions())
        droplet.load()
        print(droplet.created_at)

        action_power = droplet.power_on(return_dict=False)
        print(droplet.get_actions())
        self.__wait_actions(droplet.get_actions())
        print('Done waiting')            
        
        print(droplet.ip_address)
        self.wait_for_ssh(droplet.ip_address)

        return droplet.ip_address


    def end_instance(self):
        
        manager = digitalocean.Manager(token=self.config.TOKEN)
        droplets = manager.get_all_droplets()

        image = self.__get_latest_snapshot(manager)

        try: 
            droplet = [droplet for droplet in droplets if droplet.name == self.config.INSTANCE_NAME][0]
        except:
            raise Exception("Couldn't retrieve instance")
        
        action_power_off = droplet.power_off(return_dict=False)
        action_power_off.wait()

        action_snapshot = droplet.take_snapshot('%s_%d' % (self.config.GAME_NAME, int(time.time())), return_dict=False)
        action_snapshot.wait()

        droplet.destroy()
        image.destroy()
        print('Stopped instance')

    def erase(self):