"""
The WhatsApp bot (M6): a student links their WhatsApp number with a one-time code from the app; a class rep
forwards an announcement in a private chat and confirms (or discards) what the bot read, exactly as in the app's
rep panel; anyone linked can ask for the next 7 days (WEEK), HELP, or unlink (STOP).

Only a keyed hash of a linked number is kept, never the number: the bot replies to the number a message came
from, so it never needs to look one up. Every message from Meta is checked against the app secret's signature,
stale and repeated messages are dropped, and group messages are ignored. No money over WhatsApp: a chat is easy
for someone else to read.
"""
