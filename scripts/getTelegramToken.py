from pyrogram import Client


with Client(":memory:") as app:
    print("Your Telegram token is: ")
    print(app.export_session_string())
    print("KEEP IT SAFE! Anyone with that token has complete access to your account!")
