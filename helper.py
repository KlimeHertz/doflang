from enum import Enum

def singleton(cls):
    """
    Decorator that converts the class into a Singleton by overriding its __new__ method.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

class HarvestType(Enum):
        CLICKONLVL1 = 1
        CLICKONLVL2 = 2
        
class ressourceStatus(Enum):
        SPAWNED = 1
        ENDHARVEST = 2
        HARVESTING = 3
        NOTSPWANED = 4
        

        