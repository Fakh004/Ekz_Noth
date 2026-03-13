import uuid
from database import get_connection


def register_user(username, password):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return {"status": 200, "msg": "Registered!"}
        except:
            return {"status": 400, "msg": "User already exists"}


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()        
        print(f"Попытка входа: {username}, Найдено в базе: {dict(user) if user else 'Ничего'}")

        if user:
            new_token = str(uuid.uuid4())
            cursor.execute("INSERT INTO tokens (user_id, token) VALUES (?, ?)", (user["id"], new_token))           
            conn.commit() 
            return {"status": 200, "token": new_token, "msg": "Login success"}
        return {"status": 401, "msg": "Wrong username or password"}
    except Exception as e:
        print(f"Ошибка базы данных: {e}")
        return {"status": 500, "msg": "Internal server error"}
    finally:
        conn.close()

def logout_user(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"status": 200, "msg": "Logout success"}
    except Exception as e:
        print(f"Ошибка базы данных: {e}")
        return {"status": 500, "msg": "Internal server error"}
    finally:
        conn.close()

def create_notif(user_id, msg):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (user_id, msg))
        conn.commit()
        return {"status": 200, "msg": "Notification created!"}

def get_all_notifs():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT notifications.id, notifications.message, users.username, notifications.created_at 
            FROM notifications 
            JOIN users ON notifications.user_id = users.id
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
def delete_notification_by_id(notif_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM notifications WHERE id = ?", (notif_id,))
        if not cursor.fetchone():
            return {"status": 404, "msg": f"Notification with ID {notif_id} not found"}
        cursor.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
        conn.commit()
        return {"status": 200, "msg": f"Notification {notif_id} deleted successfully"}
    except Exception as e:
        return {"status": 500, "msg": f"Error: {e}"}
    finally:
        conn.close()