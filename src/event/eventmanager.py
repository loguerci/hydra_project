#the purpose of this class is to exchange data between two object
#given an event type (string), the object that needs to receive data calls
#the subscribe method, passing as parameter a function that must be executed
#everytime data is sent

#the sender calls the publich method passing as parameter the data

class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
