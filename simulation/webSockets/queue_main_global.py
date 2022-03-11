from eventlet.queue import Queue
# from queue import Queue
class QueueHolder:
    global_callback_queue = Queue()
    
    