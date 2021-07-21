import digitalocean
import paramiko
import time

from odgs.provider import Provider


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
        key = next(key for key in keys if key.name == self.config.SSH_KEY_NAME)
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
            droplet = next(droplet for droplet in droplets if droplet.name == self.config.INSTANCE_NAME)
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
        pass
