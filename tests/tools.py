import json
import pprint
from collections import OrderedDict

DUMP_FILE = "tests/test.txt"

resp = OrderedDict()
prev = None


def pkg(rec):
    global prev
    layers = rec['_source']['layers']
    data = layers.get('data', None)
    port = layers['tcp']['tcp.dstport']
    port = int(port)
    if data is None:
        # pprint.pprint(rec)
        return(None, port)
    data = data["data.data"]
    # print(port + 10000, ":", data)
    data = bytes.fromhex(data.replace(":", " "))
    if port != 7778:
        assert prev
        if data != "06":
            l = resp.setdefault(prev[0], [])
            if data not in l:
                l.append(data)
    else:
        prev = data, port
    return data, port


def load():
    pkgs = json.load(open(DUMP_FILE))
    print(len(pkgs))
    c = -1
    for p in pkgs:
        data, port = pkg(p)
        if data is None:
            continue
        c -= 1
        if c == 0:
            break

    # pprint.pprint(resp)
    return resp
