#!/usr/bin/env python3

# SLOW CALCULATOR
#   This calculator works by accepting the following commands, then waiting 10 seconds before performing the
#   calculation. The 'status' command can be used at any time to determine the current state of the calculator.
#   The stop command can be used at any time to stop the calculation.
#
# COMMANDS:
#   add
#   subtract
#   multiply
#   divide
#   status
#   stop
#
# EXAMPLES:
#   add,1,2         = 3
#   subtract,5,1    = 4
#   multiply,2,3    = 6
#   divide,10,2     = 5


import asyncio
import threading
import time


class Calculator:

    def __init__(self):
        self.state = 'idle'
        self.command = ''
        self.timeLeft = 0
        self.solution = 'None'
        self.abort = False

    def add(self, a, b):
        sol = a + b
        self.solution = sol
        return str(sol)

    def subtract(self, a, b):
        sol = a - b
        self.solution = sol
        return str(sol)

    def multiply(self, a, b):
        sol = a * b
        self.solution = sol
        return str(sol)

    def divide(self, a, b):
        try:
            sol = a / b
        except ZeroDivisionError:
            return 'CANNOT DIVIDE BY ZERO'
        self.solution = sol
        return str(sol)

    def status(self):
        reply = f"state={self.state}\n" \
                f"command={self.command}\n" \
                f"timeLeft={self.timeLeft}\n" \
                f"solution={self.solution}"
        return reply

    def stop(self):
        reply = ''
        if self.timeLeft != 0:
            self.timeLeft = 0
            self.abort = True
            reply = "CANCELLED"
        else:
            reply = "IDLE"

        return reply

    def count_down_time(self):
        self.timeLeft = 10
        while self.timeLeft > 0:
            time.sleep(1)
            self.timeLeft -= 1
        self.timeLeft = 0


def calculate(writer, msg):
    msgList = msg.split(",")
    reply = ''

    calc.command = msg
    calc.state = 'busy'
    calc.count_down_time()

    if calc.abort:
        calc.abort = False
    else:
        if msgList[0] == 'add':
            reply = calc.add(float(msgList[1]), float(msgList[2]))
        elif msgList[0] == 'subtract':
            reply = calc.subtract(float(msgList[1]), float(msgList[2]))
        elif msgList[0] == 'multiply':
            reply = calc.multiply(float(msgList[1]), float(msgList[2]))
        elif msgList[0] == 'divide':
            reply = calc.divide(float(msgList[1]), float(msgList[2]))

        reply = msg + ' = ' + reply + '\n'
        writer.write(reply.encode())

    calc.state = 'idle'


async def check_data(msg):
    msgList = msg.split(",")

    if len(msgList) == 1:
        if msgList[0] == 'status' or msgList[0] == 'stop':
            return ''
        else:
            return f"{msg} ERROR"

    elif len(msgList) == 3:
        if msgList[0] == 'add' or msgList[0] == 'subtract' or msgList[0] == 'multiply' or msgList[0] == 'divide':
            try:
                float(msgList[1])
                float(msgList[2])
                return f"{msg} RUNNING"

            except IndexError:
                return f"{msg} ERROR"

            except ValueError:
                return f"{msg} ERROR"

        else:
            return f"{msg} ERROR"

    else:
        return f"{msg} ERROR"


async def handle_data(reader, writer):
    reply = ''
    loop = True
    while loop:
        data = await reader.read(100)
        message = data.decode()[:-2]

        if message == 'q':
            loop = False
        else:
            check = await check_data(message)
            check = check+'\n'
            writer.write(check.encode())

            msgList = message.split(",")
            if len(msgList) == 1:
                if msgList[0] == 'status':
                    reply = calc.status()
                elif msgList[0] == 'stop':
                    reply = calc.stop()

                reply = reply + '\n'
                writer.write(reply.encode())

            else:
                comThread = threading.Thread(target=calculate, args=(writer, message,))
                comThread.start()

        await writer.drain()

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
