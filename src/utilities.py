import datetime


class LogDate:

    def __init__(self):
        """Used to create file titles for logs (each chat log file corresponds to a channel and a day),
        Also used to create timestamps for messages and whispers."""
        self.months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                       '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November',
                       '12': 'December'}
        self.date_log = datetime.datetime.now()
        self.date = str(self.date_log).split(" ")[0]
        self.month_num = self.date.split("-")[1]
        self.month = self.months[self.month_num]
        self.day = str(self.date.split("-")[2])
        self.year = str(self.date.split("-")[0])
        self.hour = str(self.date_log.hour)
        self.minute = str(self.date_log.minute)
        self.second = str(self.date_log.second)
        if len(self.second) == 1:
            self.second = "0" + self.second
        if len(self.minute) == 1:
            self.minute = "0" + self.minute
        self.timestamp = '[' + self.hour + ':' + self.minute + ':' + self.second + ']'


class PhiQueue:
    def __init__(self, initials=None, maxsize=None):
        """A simple queue-type class"""
        self.maxsize = self.config_max(maxsize)
        self.items = []
        if initials:
            self.put(initials)

    def __repr__(self):
        return str(self.items)

    def __getitem__(self, i):
        return self.items[i]

    @staticmethod
    def config_max(mx):
        if type(mx) == int:
            return abs(mx)
        return None

    def is_empty(self):
        return len(self.items) == 0

    def index(self, i):
        return self.items.index(i)

    def is_full(self):
        is_full = False
        if self.maxsize:
            if len(self.items) >= self.maxsize:
                is_full = True
        else:
            if len(self.items) >= 536870912:
                is_full = True
        return is_full

    def pop(self, i=1):
        self.items = self.items[i:]

    def put(self, i):

        if i and type(i) == list:
            for item in i:
                self.put(item)
        elif not i:
            self.items = []
        elif not self.maxsize or self.size() < self.maxsize:
            self.items.append(i)
        else:
            self.pop()
            self.put(i)

    def set_maxsize(self, i, reset=True):
        self.maxsize = self.config_max(i)
        if reset:
            items = self.items[:]  # copy original item list
            del self.items[:]
            self.put(items)

    def size(self):
        return len(self.items)


if __name__ == "__main__":
    pq = PhiQueue()
    print(pq)
