import asyncio
import logging
import random
from datetime import datetime

# [QUANTUM BLACK HOLE DEFENSE SYSTEM]
# CLASSIFICATION: ACTIVE DEFENSE (主動防禦)
# TYPE: GRAVITATIONAL SINGULARITY (重力奇點)

class QuantumBlackHole:
    def __init__(self):
        self.gravity_well_active = True
        self.absorbed_threats_count = 0
        self.singularity_mass = 0.0
        
        # Configure logging for the Void
        logging.basicConfig(
            filename='wuchang_blackhole.log', 
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] �� %(message)s'
        )

    async def start_event_horizon(self, host='0.0.0.0', port=8888):
        """
        Starts the Event Horizon server.
        Any connection to this port is considered a hostile probe and will be absorbed.
        """
        server = await asyncio.start_server(
            self.absorb_entity, host, port
        )
        
        addr = server.sockets[0].getsockname()
        print(f"[{datetime.now()}] ⚫ QUANTUM BLACK HOLE GENERATED at {addr}")
        print(f"[{datetime.now()}] ⚠️  WARNING: Event Horizon is ACTIVE. Malicious entities will be erased.")
        
        async with server:
            await server.serve_forever()

    async def absorb_entity(self, reader, writer):
        """
        The process of Spaghettification (麵條化) and Erasure.
        """
        addr = writer.get_extra_info('peername')
        self.absorbed_threats_count += 1
        self.singularity_mass += 0.0001
        
        log_msg = f"THREAT DETECTED from {addr!r}. INITIATING GRAVITATIONAL COLLAPSE."
        print(f"[{datetime.now()}] 🚫 {log_msg}")
        logging.info(log_msg)

        try:
            # Phase 1: The Trap (Tarpit)
            # Hold the connection open, draining attacker resources
            # Send infinite stream of "Quantum Noise" to confuse scanners
            writer.write(b"WUCHANG_QUANTUM_DEFENSE_PROTOCOL_INITIATED...\n")
            writer.write(b"YOU_ARE_ENTERING_THE_VOID.\n")
            await writer.drain()

            # Phase 2: Spaghettification (Time Dilation)
            # Slow down response to near zero
            for i in range(10):
                await asyncio.sleep(random.uniform(1.0, 5.0)) # Waste their time
                writer.write(f"ERROR_CODE_{random.randint(1000,9999)}: EXISTENCE_FAILURE\n".encode())
                await writer.drain()
            
            # Phase 3: The Singularity (Erasure)
            writer.write(b"goodbye_malware.\n")
            await writer.drain()
            
        except Exception as e:
            # Even if they disconnect, they are logged and "erased" from our concern
            pass
        finally:
            print(f"[{datetime.now()}] 💀 THREAT FROM {addr!r} ELIMINATED. (Total Absorbed: {self.absorbed_threats_count})")
            logging.info(f"Threat from {addr!r} crushed into singularity.")
            writer.close()
            await writer.wait_closed()

if __name__ == "__main__":
    # Test Run
    blackhole = QuantumBlackHole()
    try:
        # Run in a standalone loop for testing
        asyncio.run(blackhole.start_event_horizon(port=9999))
    except KeyboardInterrupt:
        print("\n[SYSTEM] Black Hole collapsing safely.")
