from datetime import datetime, timedelta
import sqlite3

con = sqlite3.connect("tame_management.db")

cur = con.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY, 
            title TEXT NOT NULL, 
            due_date TEXT, 
            sp REAL, 
            description TEXT,
            status TEXT,
            sprint BOOL NOT NULL)"""
)

cur.execute(
    """CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts5 USING fts5(id, title, description)"""
)

cur.execute(
    """CREATE TRIGGER insert_task_fts
    AFTER INSERT on tasks
    BEGIN
    INSERT INTO tasks_fts5 (id, title, description) VALUES (NEW.id, NEW.title, NEW.description);
    END;"""
)

cur.execute(
    """CREATE TRIGGER update_task_fts
    after UPDATE on tasks
    begin
    UPDATE tasks_fts5 SET id = NEW.id, title = NEW.title, description = NEW.description 
    WHERE id = NEW.id;
    end"""
)

cur.execute(
    """CREATE TRIGGER delete_task_fts
    after DELETE on tasks
    begin
    DELETE FROM tasks_fts5 WHERE id = OLD.id;
    end"""
)

cur.execute(
    """CREATE TABLE settings (
        id INTEGER NOT NULL PRIMARY KEY,
        name NOT NULL TEXT,
        value TEXT)"""
)
