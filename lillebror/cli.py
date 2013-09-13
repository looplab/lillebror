# Copyright (c) 2012-2013 - Max Persson <max@looplab.se>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from skal import command
import gevent

from .monitor import Monitor


@command
def server(config_file=None):
    monitor = Monitor(test_config)
    while True:
        gevent.sleep(1.0)

test_config = {
    "samplers": {
        "cpu": {
            "type": "cpu"
        },
        "memory": {
            "type": "memory"
        },
        "task_switches": {
            "type": "task_switches"
        }
    },
    "outputs": {
        "all": {
            "type": "zerorpc",
            "samplers": ["cpu", "memory", "task_switches"],
            "url": "tcp://172.20.10.3:7778"
        }
    }
}

test_config2 = {
    "samplers": {
        "cpu": {
            "type": "python",
            "code": "psutil.cpu_percent()"
        },
        "mem": {
            "type": "python",
            "code": "psutil.cpu_percent()"
        },
        "popen": {
            "type": "python",
            "code": "gevent.subprocess.call(['echo', 'test'])"
        }
    },
    "outputs": {
        "all": {
            "type": "zerorpc",
            "url": "tcp://172.20.10.3:7778"
        }
    }
}
