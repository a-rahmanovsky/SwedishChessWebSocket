import asyncio
import websockets
import json
import Board


def is_castling(begin, end):
    if begin == 'e1' and end == 'g1':
        return 'w', 'r', 's'
    if begin == 'e1' and end == 'c1':
        return 'w', 'l', 'l'
    if begin == 'e8' and end == 'g8':
        return 'b', 'r', 's'
    if begin == 'e8' and end == 'c8':
        return 'b', 'l', 'l'
    return False


class Server:
    clients = dict()
    slots = [False] * 4
    game = Board.Game()

    async def register(self, ws, login):
        if login not in self.clients:
            self.clients[login] = ws
            await asyncio.wait([ws.send(json.dumps({'status': 'OK'}))])
        else:
            await asyncio.wait([ws.send(json.dumps({'status': 'fail', 'error': 'Такой пользователь уже существует'}))])
        print(self.clients)

    async def unregister(self, ws, login):
        if login in self.clients:
            del self.clients[login]
            if login in self.slots:
                self.slots[self.slots.index(login)] = False
        print(ws.remote_address, 'disconnect')

    async def sent_to_clients(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients.values()])

    async def sent_by_login(self, login, message):
        if login in self.clients.keys():
            await asyncio.wait([self.clients[login].send(message)])

    async def ws_handler(self, ws, uri):
        login = uri[1:]
        await self.register(ws, login)
        try:
            await self.distribute(ws, login)
        finally:
            await self.unregister(ws, login)

    async def distribute(self, ws, login):
        async for message in ws:
            m_js = json.loads(message)
            print(message, login)
            if m_js['type'] == 'choose_slot':
                await self.choose_slot(m_js, login)
            if m_js['type'] == 'step':
                await self.step(m_js, login)
            if m_js['type'] == 'new_piece':
                await self.new_piece(m_js, login)
            if m_js['type'] == 'choose_piece':
                await self.change_pawn(m_js, login)

    async def choose_slot(self, m_js, login):
        slot = int(m_js['slot'])
        if self.slots[slot]:
            await self.sent_by_login(login, json.dumps({'type': 'choose_slot', 'status': 'Fail'}))
        else:
            self.slots[slot] = login
            await self.sent_by_login(login, json.dumps({'type': 'choose_slot', 'status': 'OK'}))
        if self.slots.count(False) == 3:
            self.game = Board.Game()
        if False not in self.slots:
            await self.sent_to_clients(json.dumps({'type': 'init', 'players': self.slots}))

    async def step(self, m_js, login):
        index = self.slots.index(login)
        begin = m_js['from']['h'] + str(m_js['from']['v'])
        end = m_js['to']['h'] + str(m_js['to']['v'])
        num_board = 0 if index == 0 or index == 2 else 1
        castling = is_castling(begin, end)
        if castling:
            res = self.game.castling(num_board, castling[0], castling[1])
            if res == '.':
                m_js['login'] = login
                m_js['turn'] = 'white'
                if self.game.get_color(num_board) == 'b':
                    m_js['turn'] = 'black'
                m_js['type_castling'] = castling[2]
                m_js['is_castling'] = True
                await self.sent_to_clients(json.dumps(m_js))
            else:
                await self.sent_by_login(login, json.dumps({'type': 'invalid_step'}))
        else:
            figure = self.game.move(num_board, begin, end)
            if figure not in '+.!?':
                new_index = 1
                if index == 2:
                    new_index = 3
                if index == 1:
                    new_index = 0
                if index == 3:
                    new_index = 2
                login_send = self.slots[new_index]
                await self.sent_by_login(login_send, json.dumps({'type': 'add_piece', 'piece': figure}))
            if figure == '+':
                await self.sent_by_login(login, json.dumps({'type': 'pawn_wire', 'from': m_js['from'], 'to': m_js['to']}))
            if figure not in '+!?':
                m_js['login'] = login
                m_js['turn'] = 'white'
                if self.game.get_color(num_board) == 'b':
                    m_js['turn'] = 'black'
                print(f'before send {self.game.get_color(num_board)}')
                await self.sent_to_clients(json.dumps(m_js))
            elif figure in '?!':
                await self.sent_by_login(login, json.dumps({'type': 'invalid_step'}))

    async def new_piece(self, m_js, login):
        position = m_js['position']
        if position == 'offboard':
            return
        figure = m_js['piece_type']
        index = self.slots.index(login)
        color = 'b' if index == 1 or index == 2 else 'w'
        num_board = 0 if index == 0 or index == 2 else 1
        result = self.game.add_figure(num_board, position, figure, color)
        print(num_board, result, self.game.get_color(num_board))
        if result not in '!?':
            m_js['login'] = login
            m_js['turn'] = 'white'
            if self.game.get_color(num_board) == 'b':
                m_js['turn'] = 'black'
            await self.sent_to_clients(json.dumps(m_js))
        else:
            await self.sent_by_login(login, json.dumps({'type': 'invalid_step'}))

    async def change_pawn(self, m_js, login):
        end = m_js['to']['h'] + str(m_js['to']['v'])
        index = self.slots.index(login)
        num_board = 0 if index == 0 or index == 2 else 1
        turn = 'white'
        if self.game.get_color(num_board) == 'b':
            turn = 'black'
        response = json.dumps({'type': 'step_pawn_wire',
                               'login': login,
                               'pawn': m_js['from'],
                               'new_piece_position': m_js['to'],
                               'turn': turn,
                               'piece_type': m_js['piece']
                               })
        print(f'recw: {m_js}')
        print(f'send: {response}')
        await self.sent_to_clients(response)


server = Server()
start_server = websockets.serve(server.ws_handler, '0.0.0.0', 5000)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
