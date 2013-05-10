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
