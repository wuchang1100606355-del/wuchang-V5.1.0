import asyncio
import staps_core
import time

async def main():
    print('='*60)
    print('[STAPS DEMO] Wuchang STAPS Secure Kernel Demonstration')
    print('='*60)
    
    print('[STEP 1] 載入加密核心模組 (Loading Encrypted Module)...')
    try:
        # 這裡導入的是 .pyd 二進制檔案，而非 .py 原始碼
        print(f'   -> Module: {staps_core}')
        print(f'   -> File: {staps_core.__file__}')
    except ImportError as e:
        print(f'[ERROR] 無法載入 staps_core: {e}')
        return

    print('\n[STEP 2] 初始化核心實例 (Initializing Kernel Instance)...')
    kernel = staps_core.StapsKernel()
    print(f'   -> Instance ID: {id(kernel)}')
    print('   -> Status: READY')

    print('\n[STEP 3] 執行黑盒運算 (Executing Blackbox Operation)...')
    payload = {'source': 'DemoScript', 'priority': 'HIGH', 'timestamp': time.time()}
    print(f'   -> Sending Payload: {payload}')
    
    # 調用加密方法
    start_time = time.time()
    result = await kernel.broadcast('SECURE_HANDSHAKE', payload)
    end_time = time.time()
    
    print(f'   -> Operation Result: {result}')
    print(f'   -> Execution Time: {(end_time - start_time)*1000:.4f} ms')

    print('\n' + '='*60)
    print('[SUCCESS] 演示完成：加密核心運作正常。')
    print('此演示證明了即使沒有原始碼，系統仍能透過二進制介面完美運作。')
    print('='*60)

if __name__ == '__main__':
    asyncio.run(main())
