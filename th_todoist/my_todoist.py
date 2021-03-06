# coding: utf-8

# TodoistAPI
from todoist import TodoistAPI

# django classes
from django.conf import settings
from django.utils.log import getLogger
from django.core.cache import caches

# django_th classes
from django_th.services.services import ServicesMgr


"""
    handle process with todoist
    put the following in settings.py

    TH_TODOIST = {
        'client_id': 'abcdefghijklmnopqrstuvwxyz',
        'client_secret': 'abcdefghijklmnopqrstuvwxyz',
    }
    TH_SERVICES = (
        ...
        'th_todoist.my_todoist.ServiceTodoist',
        ...
    )
"""

logger = getLogger('django_th.trigger_happy')

cache = caches['th_todoist']


class ServiceTodoist(ServicesMgr):

    def __init__(self, token=None, **kwargs):
        super(ServiceTodoist, self).__init__(token, **kwargs)
        self.AUTH_URL = 'https://todoist.com/oauth/authorize'
        self.ACC_TOKEN = 'https://todoist.com/oauth/access_token'
        self.REQ_TOKEN = 'https://todoist.com/oauth/access_token'
        self.consumer_key = settings.TH_TODOIST['client_id']
        self.consumer_secret = settings.TH_TODOIST['client_secret']
        self.scope = 'task:add,data:read,data:read_write'
        self.service = 'ServiceTodoist'
        self.oauth = 'oauth2'
        if token:
            self.token = token
            self.todoist = TodoistAPI(token)

    def read_data(self, **kwargs):
        """
            get the data from the service
            as the pocket service does not have any date
            in its API linked to the note,
            add the triggered date to the dict data
            thus the service will be triggered when data will be found

            :param kwargs: contain keyword args : trigger_id at least
            :type kwargs: dict

            :rtype: list
        """
        trigger_id = kwargs['trigger_id']
        data = list()
        cache.set('th_todoist_' + str(trigger_id), data)

    def save_data(self, trigger_id, **data):
        """
            let's save the data
            :param trigger_id: trigger ID from which to save data
            :param data: the data to check to be used and save
            :type trigger_id: int
            :type data:  dict
            :return: the status of the save statement
            :rtype: boolean
        """
        kwargs = {}

        title, content = super(ServiceTodoist, self).save_data(trigger_id,
                                                               data, **kwargs)

        if self.token:
            if title or content or \
                            (data.get('link') and len(data.get('link'))) > 0:
                content = title + ' ' + content + ' ' + data.get('link')

                self.todoist.add_item(content)

                sentence = str('todoist {} created').format(data.get('link'))
                logger.debug(sentence)
                status = True
            else:
                status = False
        else:
            logger.critical("no token or link provided for "
                            "trigger ID {} ".format(trigger_id))
            status = False
        return status
