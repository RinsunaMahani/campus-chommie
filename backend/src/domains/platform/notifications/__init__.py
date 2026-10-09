"""
notifications -- alerts the server makes when something happens that a
student should know about (above all when SOMEONE ELSE acts), stored with
their read state in one inbox.

Publishers never import this: they call shared.notifications
.publish_notification(), and this feature's service is the listener.
"""
