import asyncio

class NeuralSignal:
    def __init__(self, data):
        self.data = data

class StapsKernel:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StapsKernel, cls).__new__(cls)
        return cls._instance

    async def broadcast(self, intent, payload):
        print(f"[STAPS KERNEL] Received broadcast: intent={intent}, payload={payload}")
        return True

