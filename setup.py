from glob import glob

def start_setup():
    if glob("WIFI_CONFIG.py"):
        return
    
    from network_manager import NetworkManager
    import uasyncio
    import gc

    network_manager = NetworkManager()
    uasyncio.get_event_loop().run_until_complete(network_manager.access_point())
    gc.collect()
