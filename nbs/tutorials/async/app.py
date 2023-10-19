import asyncio

async def go_next():
    await asyncio.sleep(1)
    print('hello world after delay')
    loop.stop()

async def main():
    asyncio.create_task(go_next())

if __name__ == '__main__':
    print('beginning of main')
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())  # Schedule main() to run
    loop.run_forever()
    print('end of main')
