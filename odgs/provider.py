import time

from odgs.config import ssh, ssh_key


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
