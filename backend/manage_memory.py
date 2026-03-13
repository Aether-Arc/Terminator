import sqlite3
import os
import sys

DB_PATH = os.path.join(os.getcwd(), "memory", "swarm_threads.sqlite")

def connect_db():
    if not os.path.exists(DB_PATH):
        print("Database not found. It might be empty or already deleted.")
        sys.exit(0)
    return sqlite3.connect(DB_PATH)

def list_threads():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # LangGraph stores thread IDs in the 'checkpoints' table
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = cursor.fetchall()
        if not threads:
            print("No history found. The database is empty.")
            return

        print("\n--- 🧠 SAVED SWARM THREADS ---")
        for i, (thread_id,) in enumerate(threads):
            print(f"[{i}] {thread_id}")
        print("------------------------------\n")
        return [t[0] for t in threads]
    except sqlite3.OperationalError:
        print("Database is empty or tables are not created yet.")
        return []

def delete_thread(thread_id):
    conn = connect_db()
    cursor = conn.cursor()
    tables = ["checkpoints", "checkpoint_metadata", "checkpoint_blobs", "checkpoint_writes"]
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))
        except sqlite3.OperationalError:
            pass # Table might not exist yet depending on LangGraph version
            
    conn.commit()
    print(f"✅ Successfully purged thread: {thread_id}")

def wipe_all():
    confirm = input("⚠️ WARNING: This will delete ALL memory. Type 'YES' to confirm: ")
    if confirm == "YES":
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            cursor.execute(f"DROP TABLE {table_name[0]}")
        conn.commit()
        print("💥 Database completely wiped. Swarm memory is at Zero.")
    else:
        print("Aborted.")

if __name__ == "__main__":
    print("1. List all threads")
    print("2. Delete a specific thread")
    print("3. Wipe ALL history (Zero Point)")
    
    choice = input("\nSelect an option (1/2/3): ")
    
    if choice == "1":
        list_threads()
    elif choice == "2":
        threads = list_threads()
        if threads:
            idx = int(input("Enter the [number] of the thread to delete: "))
            if 0 <= idx < len(threads):
                delete_thread(threads[idx])
            else:
                print("Invalid selection.")
    elif choice == "3":
        wipe_all()
    else:
        print("Invalid choice.")