# Copyright 2013 Loop Lab
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


import os
import datetime
import csv

import gevent
import zerorpc


def make_output(dct, all_samplers):
    samplers = {}
    for name, sampler in all_samplers.iteritems():
        # TODO: Needs to be added in order here
        if (not 'samplers' in dct) or (name in dct['samplers']):
            samplers[name] = sampler

    output = None
    if dct['type'] == 'csv':
        output = CSVOutput(samplers, dct['path'], dct['start_time'])
    elif dct['type'] == 'zerorpc':
        output = ZeroRPCOutput(samplers, dct['url'])

    return output


class BaseOutput(object):
    def __init__(self, samplers):
        self._samplers = samplers
        self._kill_flag = False
        self._output_task = None

    def start(self):
        self._output_task = gevent.spawn(self._output)
        self._output_task.link(self._stop)

    def stop(self):
        self._kill_flag = True

    def _stop(self, task):
        pass

    def _output(self):
        while not self._kill_flag:
            for name, sampler in self._samplers.iteritems():
                sampler.sample()
            self._do_output()
            gevent.sleep(1.0)

    def _do_output(self):
        raise NotImplementedError


class CSVOutput(BaseOutput):
    def __init__(self, samplers, path, start_time):
        super(CSVOutput, self).__init__(samplers)
        self._path = path
        self._start_time = start_time
        self._file = None
        self._writer = None

    def start(self):
        if self._path:
            self._file = open(self._path, 'w')
            self._writer = csv.writer(self._file)
            self._writer.writerow(('time', 'cpu', 'memory', 'task_switches'))
            self._file.flush()
            os.fsync(self._file.fileno())
        super(CSVOutput, self).start()

    def _stop(self, task):
        if self._file:
            self._file.close()

    def _do_output(self):
        # for name, sampler in self._samplers.iteritems():
        #     values.append(sampler.value)
        time = datetime.datetime.now() - self._start_time
        values = [
            int(time.total_seconds()),
            int(self._samplers['cpu'].value),
            int(self._samplers['memory'].value),
            int(self._samplers['task_switches'].value)
        ]

        if self._path:
            self._writer.writerow(values)
            self._file.flush()
            os.fsync(self._file.fileno())


class ZeroRPCOutput(BaseOutput):
    def __init__(self, samplers, url):
        super(ZeroRPCOutput, self).__init__(samplers)
        self._url = url
        self._client = zerorpc.Client()

    def start(self):
        self._client.connect(self._url)
        super(ZeroRPCOutput, self).start()

    def _do_output(self):
        dct = {}
        for name, sampler in self._samplers.iteritems():
            dct[name] = sampler.value
        self._client.set_sample(dct)
