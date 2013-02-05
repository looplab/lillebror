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


import os
import collections
import datetime
import csv

import gevent
import psutil


class Monitor(object):
    def __init__(self, start_time, monitor_path, pid=None):
        self._pid = pid
        self._process = None
        self._start_time = start_time
        self._monitor_path = monitor_path
        self._samplers = []
        self._kill_flag = False
        self._monitor_task = gevent.spawn(self._monitor)
        self._monitor_task.link(self._monitor_stop)

    def stop(self):
        self._kill_flag = True

    def _monitor(self):
        if not self._pid:
            self._pid = os.getpid()

        if self._monitor_path:
            try:
                self._process = psutil.Process(self._pid)
            except psutil.NoSuchProcess:
                return
                # self.LOG.warning(
                #     'failed to start system monitor, process already finished')

        # TODO: Add samplers with a factory instead
        if self._process:
            self._samplers.append(CPUSampler(self._process))
            self._samplers.append(MemorySampler(self._process))
            self._samplers.append(SwitchSampler(self._process))

        # TODO: Add outputs with a factory instead
        # TODO: Make output columns depend on the added samplers
        self._file = open(self._monitor_path, 'w')
        self._writer = csv.writer(self._file)
        self._writer.writerow(('Sec', 'CPU', 'Memory', 'Switches'))

        while not self._kill_flag:
            time = datetime.datetime.now() - self._start_time
            for sampler in self._samplers:
                sampler.sample()
            values = [int(s.value) for s in self._samplers]
            # TODO: Make better output handling
            self._writer.writerow((
                int(time.total_seconds()),
                values[0],
                values[1],
                values[2]))
            gevent.sleep(0.1)

    def _monitor_stop(self, task):
        if self._file:
            self._file.close()


class BaseSampler(object):
    def __init__(self, process):
        self._process = process
        self._samples = collections.deque(maxlen=10)
        self.value = 0.0

    def _calc_average(self):
        if self._samples:
            s = sum(self._samples)
            self.value = s / float(len(self._samples))

    def sample(self):
        try:
            child_processes = self._process.get_children(recursive=True)
        except psutil.NoSuchProcess:
            return

        s = 0.0
        for p in child_processes:
            new_s = self._get_sample(p)
            if new_s:
                s += new_s

        self._samples.append(s)
        self._calc_average()


class CPUSampler(BaseSampler):
    def _get_sample(self, p):
        try:
            return p.get_cpu_percent(0)
        except psutil.AccessDenied:
            pass


class MemorySampler(BaseSampler):
    def _get_sample(self, p):
        try:
            return p.get_memory_info()[0]
        except psutil.AccessDenied:
            pass


class SwitchSampler(BaseSampler):
    def __init__(self, sampler):
        super(SwitchSampler, self).__init__(sampler)
        self._prev = 0

    def _get_sample(self, p):
        try:
            sample = p.get_num_ctx_switches()[0]
            new = sample - self._prev
            self._prev = sample
            return new
        except psutil.AccessDenied:
            pass
