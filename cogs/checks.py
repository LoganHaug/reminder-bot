import database
import sqlite3


def is_administrator(ctx):
    return ctx.message.author.id == 322158695184203777


def is_operator(ctx):
    """Returns whether the user of the context is an operator of the bot"""
    conn = sqlite3.connect("reminder_bot.db")
    cursor = conn.cursor()
    user = cursor.execute("SELECT * from users").fetchall()
    conn.close()
    return user != []
