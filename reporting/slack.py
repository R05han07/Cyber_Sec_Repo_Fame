import json

from fame.common.exceptions import ModuleInitializationError
from fame.core.module import ReportingModule

try:
    import requests

    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False

try:
    from defang import defang

    HAVE_DEFANG = True
except ImportError:
    HAVE_DEFANG = False


class Slack(ReportingModule):
    name = "slack"
    description = "Post message on Slack when an anlysis if finished."

    config = [
        {"name": "url", "type": "str", "description": "Incoming webhook URL."},
        {
            "name": "fame_base_url",
            "type": "str",
            "description": "Base URL of your FAME instance, as you want it to appear in links.",
        },
    ]

    def initialize(self):
        if ReportingModule.initialize(self):
            if not HAVE_REQUESTS:
                raise ModuleInitializationError(self, "Missing dependency: requests")

            if not HAVE_DEFANG:
                raise ModuleInitializationError(self, "Missing dependency: defang")

            return True
        else:
            return False

    def done(self, analysis):

        string = "Just finished analysis on {0}\n".format(
            defang(", ".join(analysis._file["names"]))
        )

        if analysis["modules"]:
            string += "Target: {}\n".format(', '.join(analysis['modules']))

        if analysis["extractions"]:
            string += "Extractions: {}\n".format(', '.join([x['label'] for x in analysis['extractions']]))

        if analysis["probable_names"]:
            string += "Probable Names: {}\n".format(', '.join(analysis['probable_names']))

        string += "<{}/analyses/{}|See analysis>".format(self.fame_base_url, analysis['_id'])

        data = {"text": string}
        requests.post(self.url, data={"payload": json.dumps(data)})
