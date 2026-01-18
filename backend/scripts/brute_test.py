import sqlalchemy
from sqlalchemy import create_engine, text
import sys

def try_conn(user, password, dbname):
    for host in ["localhost", "127.0.0.1"]:
        url = f"postgresql://{user}:{password}@{host}:5432/{dbname}"
        try:
            engine = create_engine(url, connect_args={"connect_timeout": 2})
            with engine.connect() as conn:
                print(f"SUCCESS: {user} / {password} / {dbname} on {host}")
                try:
                    res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = \"vector\""))
                    if res.fetchone():
                        print("  Vector extension: AVAILABLE")
                    else:
                        print("  Vector extension: NOT AVAILABLE")
                except Exception as e:
                    print(f"  Could not check extensions: {e}")
                return True
        except Exception as e:
            pass
    return False

if __name__ == "__main__":
    users = ["milind", "postgres", "Milind"]
    pwds = ["", "password"]
    dbs = ["hivemind", "postgres"]
    found = False
    for u in users:
        for p in pwds:
            for d in dbs:
                if try_conn(u, p, d):
                    found = True
    if not found:
        print("All connection attempts failed.")
        sys.exit(1)
