import rpyc
import sys

host = "localhost"
port = 18812

try:
    conn = rpyc.connect(host, port, timeout=10)
    is_dead = int(not conn.root.is_alive())
    conn.close()

    sys.exit(is_dead)
except Exception as e:
    sys.exit(1)