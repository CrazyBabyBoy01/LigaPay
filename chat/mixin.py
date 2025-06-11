# chat/mixins.py

from datetime import timedelta

class GroupedMessagesMixin:
    def group_messages(self, messages):
        grouped = []
        current_group = None

        for msg in messages:
            if current_group is None:
                current_group = {
                    "sender": msg.sender,
                    "timestamp": msg.timestamp,
                    "messages": [msg.message],
                }
            else:
                last_time = current_group["timestamp"]
                if msg.sender == current_group["sender"] and (msg.timestamp - last_time) <= timedelta(minutes=1):
                    current_group["messages"].append(msg.message)
                    current_group["timestamp"] = msg.timestamp
                else:
                    grouped.append(current_group)
                    current_group = {
                        "sender": msg.sender,
                        "timestamp": msg.timestamp,
                        "messages": [msg.message],
                    }

        if current_group:
            grouped.append(current_group)

        return grouped
