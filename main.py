#!/usr/bin/env python3

import asyncio
import threading


class Calculator:

    def __init__(self):
        self.state = 'idle'
        self.command = ''
        self.timeLeft = 0
        self.solution = 'None'

    def add(self, a, b):
        self.command = f"{a} + {b}"
        sol = a + b
        self.solution = sol
        return sol

    def subtract(self, a, b):
        self.command = f"{a} - {b}"
        sol = a - b
        self.solution = sol
        return sol

    def multiply(self, a, b):
        self.command = f"{a} * {b}"
        sol = a * b
        self.solution = sol
        return sol

    def divide(self, a, b):
        self.command = f"{a} // {b}"
        sol = a / b
        self.solution = sol
        return sol

    def status(self):
        reply = f"state={self.state}\n" \
                f"command={self.comand}\n" \
                f"timeLeft={self.timeLeft}\n" \
                f"solution={self.solution}"
        return reply

    def stop(self):
        reply = f"{self.command} CANCELLED"
        return reply


async def check_data(msg):
    msgList = msg.split(",")
    reply = f"{msg} ERROR"

    if len(msgList) == 1:
        if msgList[0] == 'status':
            reply = calc.status()
            return reply

        elif msgList[0] == 'stop':
            reply = calc.stop()
            return reply

        else:
            reply = f"{msg} ERROR"
            return reply

    elif len(msgList) == 3:
        if msgList[0] == 'add':
            calc.add(msgList[1], msgList[2])

        elif msgList[0] == 'subtract':
            calc.subtract(msgList[1], msgList[2])

        elif msgList[0] == 'multiply':
            calc.multiply(msgList[1], msgList[2])

        elif msgList[0] == 'divide':
            calc.divide(msgList[1], msgList[2])

        else:
            reply = f"{msg} ERROR"
            return reply

    else:
        reply = f"{msg} ERROR"
        return reply

    return reply


async def handle_data(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    reply = await check_data(message)

    reply = reply + '\r\n>'
    print(f"Send: {reply!r}")
    writer.write(reply.encode())
    await writer.drain()
    writer.close()


async def main():
    server = await asyncio.start_server(handle_data, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    calc = Calculator()
    asyncio.run(main())
