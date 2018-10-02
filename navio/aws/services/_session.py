import boto3
import threading


class AWSSession(object):

    def __init__(self, profile_name, region_name=None):
        self.profile_name = profile_name
        self.region_name = region_name
        self._thread_local = threading.local()
        self._thread_local.boto3_sessions = dict()

    def __session(self):
        sessions = self._thread_local.boto3_sessions
        session_key = '{profile}.{region}'.format(
            profile=self.profile_name,
            region=self.region_name
          )

        if session_key not in sessions:
            if self.profile_name in boto3.session.Session().available_profiles:
                if self.region_name:
                    sessions[session_key] = boto3.session.Session(
                        profile_name=self.profile_name,
                        region_name=self.region_name
                    )
                else:
                    sessions[session_key] = boto3.session.Session(
                        profile_name=self.profile_name)
        else:
            raise Exception('Profile not available: {}'.format(profile_name))

        return sessions[session_key]

    def client(self, name):
        return self.__session().client(name)

    def resource(self, name):
        return self.__session().resource(name)
