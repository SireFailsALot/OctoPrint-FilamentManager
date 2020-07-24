# coding=utf-8

__author__ = "Sven Lohrmann <malnvenshorn@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2017 Sven Lohrmann - Released under terms of the AGPLv3 License"

from threading import Thread
from select import select as wait_ready
from sqlalchemy import create_engine, text, exc
try:
    from psycopg2 import OperationalError, InterfaceError
except:
    pass
from sqlalchemy.exc import InterfaceError as exc_InterfaceError, OperationalError as AlchemyOpperationalError

class PGNotify(object):

    def __init__(self, uri):
        self.subscriber = list()

        # engine = create_engine(uri, pool_pre_ping=True)
        # conn = engine.connect()
        # conn.execute(text("LISTEN profiles; LISTEN spools;").execution_options(autocommit=True))

        # Modified to point to notify thread and to pass the uri as argument instead of conn. SFAL 06/27/2020
        notify_thread = Thread(target=self.notify_thread, args=(uri,))
        notify_thread.daemon = True
        notify_thread.start()

    def notify_thread(self, uri):
        # SFAL 06/27/2020 created function and modified engine to use pool_pre_ping
        '''
        The function serves as an extenstion of notify. If the notify funtion stops, well,
        functioning, this function will attempt to correct the behavior. This is inteded to add
        auto recconect functionality, should the database go down for some reason.
        :param uri:
        :return:
        '''
        engine = create_engine(uri, pool_pre_ping=True)
        conn = engine.connect()

        while True:
            try:
                conn.execute(text("LISTEN profiles; LISTEN spools;").execution_options(autocommit=True))
                self.notify(conn)
            except (
                    OperationalError,
                    InterfaceError,
                    exc_InterfaceError
                    ) as e:
                # print("Server disconnected...")
                pass
            except AlchemyOpperationalError as e:
                # print("The server appears to have shutdown. Attempting to reconnect...")
                pass
            finally:
                from time import sleep
                # Wait 5 seconds be fore reconnecting this thread, to give the server/network time to recover.
                sleep(5)


    def notify(self, conn):
        while True:
            if wait_ready([conn.connection], [], [], 5) != ([], [], []):
                conn.connection.poll()
                while conn.connection.notifies:
                    notify = conn.connection.notifies.pop()
                    for func in self.subscriber:
                        func(pid=notify.pid, channel=notify.channel, payload=notify.payload)

    def subscribe(self, func):
        self.subscriber.append(func)

    def unsubscribe(self, func):
        self.subscriber.remove(func)
