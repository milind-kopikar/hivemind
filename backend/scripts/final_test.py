from sqlalchemy import create_engine, text
import sys

def test():
    user = "milind"
    db = "hivemind"
    hosts = ["127.0.0.1", "localhost"]
    pwds = ["", "password"]
    
    for host in hosts:
        for pwd in pwds:
            url = f"postgresql://{user}:{pwd}@{host}:5432/{db}"
            print(f"Trying: {url}")
            try:
                engine = create_engine(url, connect_args={"connect_timeout": 2})
                with engine.connect() as conn:
                    print("  SUCCESS!")
                    res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
                    ext = res.fetchone()
                    if ext:
                        print("  Vector extension is AVAILABLE.")
                    else:
                        print("  Vector extension is NOT AVAILABLE.")
                    return
            except Exception as e:
                print(f"  FAILED: {e}")

if __name__ == "__main__":
    test()
