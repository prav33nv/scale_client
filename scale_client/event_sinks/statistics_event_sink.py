from scale_client.applications.statistics_application import StatisticsApplication
from scale_client.event_sinks.event_sink import EventSink

import logging
log = logging.getLogger(__name__)


class StatisticsEventSink(StatisticsApplication, EventSink):
    """
    An EventSink version of the StatisticsApplication that filters over its subscriptions and accepts only them
    for sinking.
    """

    def subscribe(self, topic, callback=None):
        """
        Does nothing to prevent actual subscribing to the topics: this class is supposed to only receive events
        to be sunk!
        :param topic:
        :param callback:
        :return:
        """
        pass

    def check_available(self, event):
        """
        Filters the events by ensuring we only sink ones for which we're gathering stats.
        :param event:
        :return:
        """
        return event.topic in self.stats

    def send_event(self, event):
        return self._analyze_event(event, event.topic)