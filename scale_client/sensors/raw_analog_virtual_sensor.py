from __future__ import print_function

from scale_client.sensors.analog_virtual_sensor import AnalogVirtualSensor
from scale_client.core.sensed_event import SensedEvent


class RawAnalogVirtualSensor(AnalogVirtualSensor):
    def __init__(self, broker, device=None, analog_port=None):
        AnalogVirtualSensor.__init__(self, broker, device=device, analog_port=analog_port)

    def get_type(self):
        return "raw_analog"

    def read(self):
        event = super(RawAnalogVirtualSensor, self).read()
        event.data['condition'] = self.__get_condition()
        return event

    def __get_condition(self):
        return {}

    def policy_check(self, data):
        data = float(data.get_raw_data())
        success = True

        return success
