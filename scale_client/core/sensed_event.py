import json
import time
import copy
from circuits import Event
import pprint

DEFAULT_PRIORITY = 5

class SensedEvent(Event):
    """
    A SensedEvent is the basic piece of data in the whole system.  Various sensors create SensedEvents
    from raw physical phenomena or other SensedEvents.  A SensedEvent mainly consists of just some data
    representing the real-world event, an identifier for what Sensor it came from, and a priority and
    timestamp value.
    """
    def __init__(self, sensor, data, priority=DEFAULT_PRIORITY, timestamp=None):
        # CIRCUITS-SPECIFIC: in order for callbacks registered via Application.subscribe to work,
        # their parameters must match those used to create the Event being fired.  Hence, we need
        # to pass the SensedEvent itself into Event's constructor in order to get the SensedEvent
        # passed into those callbacks.
        super(SensedEvent, self).__init__(self)

        # TODO: polymorphic lazy version of this object?
        self.sensor = sensor            # Sensor identifier

        if type(priority) != type(0):
            raise TypeError
        self.priority = priority        # Smaller integer for higher priority

        # we must ensure that the SensedEvent's data follows a convention of being a dict-like object
        # and that it contains the necessary fields
        # TODO: we should do away with this and figure out how to support different schemas
        try:
            str(data['value'])
            str(data['event'])
        except TypeError:
            data = {"event": "unknown_event_type", "value": data}
        except KeyError:
            old_data = data
            data["old_data"] = old_data
            data['value'] = data.get('value', "MISSING VALUE")
            data['event'] = data.get('event', "unknown_event_type")
        self.data = data                # Some abstract data that describes the event

        # timestamp defaults to right now
        if timestamp is None:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp

    def get_raw_data(self):
        """
        This function tries to intelligently extract just the raw reading from the possibly-nested self.data attribute,
        which may include other information such as units, etc.
        :return: raw data
        """
        data = self.data #data = self.data['value']
        try:
            return data['value']
        except TypeError:
            return data
        except KeyError:
            return data

    def set_raw_data(self, raw_value):
        try:
            self.data['value'] = raw_value
        except ValueError:
            self.data = raw_value

    def get_type(self):
        """
        This function tries to intelligently extract the type of SensedEvent as a string.
        :return: event type
        """
        return self.data['event']

    def set_type(self, new_type):
        """
        This function tries to intelligently mutate the type of SensedEvent to the given string.
        :return: event type
        """
        self.data['event'] = new_type

    def __repr__(self):
        s = "SensedEvent (%s) with value %s" % (self.get_type(), str(self.get_raw_data()))
        s += '\n' + pprint.pformat(self.data, width=1)
        return s

    def to_map(self):
        ret = copy.copy(self.data)

        ret["timestamp"] = self.timestamp
        ret["prio_value"] = self.priority

        if self.priority >= 0 and self.priority < 4:
            ret["prio_class"] = "high"
        elif self.priority >=7 and self.priority <= 10:
            ret["prio_class"] = "low"
        elif self.priority >= 4 and self.priority < 7:
            ret["prio_class"] = "medium"

        return ret

    def to_json(self):
        return json.dumps({"d": self.to_map()})

    @classmethod
    def from_json(cls, json_data):
        """
        Creates a SensedEvent from a raw JSON-encoded string
        :param json_data:
        :return:
        """

        ev_map = json.loads(json_data)
        try:  # removing the 'd' from the outside if it's there
            ev_map = ev_map['d']
        except KeyError:
            pass
        return cls.from_map(ev_map)

    @classmethod
    def from_map(cls, map_data):
        """
        Creates a SensedEvent from a simple map of that events' attributes as per the SCALE event schema.
        :param map_data:
        :type map_data: dict
        :return:
        """
        sensor = map_data.pop('device', 'unknown_device')
        priority = map_data.pop('prio_value', DEFAULT_PRIORITY)
        timestamp = map_data.pop('timestamp', None)
        return cls(sensor, map_data, priority, timestamp)