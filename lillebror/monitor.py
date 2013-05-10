# Copyright 2012 Loop Lab
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


import gevent

from samplers import make_sampler
from outputs import make_output


default_config = {
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
            "type": "csv",
            "samplers": ["cpu", "memory", "task_switches"],
            "path": "/Users/max/Development/otis/tmp",
            "start_time": 1000
        }
    }
}


class Monitor(object):
    def __init__(self, config=default_config):
        self._config = config

        self._samplers = {}
        for name, dct in self._config['samplers'].iteritems():
            sampler = make_sampler(dct)
            if sampler:
                self._samplers[name] = sampler

        self._outputs = {}
        for name, dct in self._config['outputs'].iteritems():
            output = make_output(dct, self._samplers)
            if output:
                self._outputs[name] = output

        self._kill_flag = False
        self._monitor_task = gevent.spawn(self._monitor)

    def stop(self):
        self._kill_flag = True

    def _monitor(self):
        for name, output in self._outputs.iteritems():
            output.start()

        while not self._kill_flag:
            gevent.sleep(0.1)

        for name, output in self._outputs.iteritems():
            output.stop()
