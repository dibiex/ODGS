from odgs.config import Config
from odgs.providers.digitalocean import DigitalOcean

if __name__ =="__main__":
    config = Config()
    provider = DigitalOcean(config)
    provider.create_instance()