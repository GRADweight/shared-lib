import sys, tempfile, os
sys.path.insert(0, os.environ.get("GW_SHARED", "."))
from gw_shared_lib.audit import audit_action
tmp = tempfile.mkdtemp()
os.chdir(tmp)
e = audit_action("./t.jsonl", "rechnung_parsed",
                 actor="demo", invoice_nr="A1", total="100",
                 supplier="Muster AG")
d = e.to_dict()
print("invoice_nr in data:", d.get("data", {}).get("invoice_nr") == "A1")
print("supplier in data:  ", d.get("data", {}).get("supplier") == "Muster AG")
print("known field ok:    ", d.get("actor") == "demo", d.get("action") == "rechnung_parsed")
print("PASS" if (d.get("data", {}).get("invoice_nr") == "A1"
                 and d.get("actor") == "demo") else "FAIL")
