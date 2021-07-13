from ods.config import Config
from ods.provider import DigitalOcean

if __name__ =="__main__":
    config = Config()
    provider = DigitalOcean(config)
    provider.create_instance()