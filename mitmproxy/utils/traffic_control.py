import subprocess
import json


class TrafficControl:

    def __init__(self, interface='eth0'):
        self.interface = interface

    # 内部方法，用于执行命令
    def _execute(self, command):
        print(command)
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # if process.returncode != 0:
        #     raise Exception(f"执行命令失败: {command}. 错误: {process.stderr}")
        return process.stdout

    # 检查是否已经存在netem规则
    def _check_netem_exists(self):
        check_command = f"tc qdisc show dev {self.interface}"
        check_output = self._execute(check_command)
        return "netem" in check_output

    # 移除现有的流量控制规则并恢复MTU
    def remove(self):
        if self._check_netem_exists():
            del_command = f"tc qdisc del dev {self.interface} root"
            self._execute(del_command)
        command = f"ip link set dev {self.interface} mtu 1500"  # 1500是大多数网络设备的默认MTU值
        self._execute(command)

    # 根据 JSON 配置文件配置网络特性
    def configure(self, config):
        config = {
            'bandwidth': {
                'up': config['uplinkBandwidth'],
                'down': config['downlinkBandwidth']
            },
            'latency': config['networkDelay'],
            'mtu': config['mtu'],
            'packet_loss': config['packetLossRate'],
            'unrestricted_ports': config['unrestrictedPorts']
        }
        self.remove()
        if 'bandwidth' in config:
            self.set_bandwidth(config['bandwidth'], config.get('unrestricted_ports', []))
        if 'mtu' in config:
            self.set_mtu(config['mtu'])
        if 'latency' in config and 'packet_loss' in config:
            self.set_latency_and_packet_loss(config['latency'], config['packet_loss'])
    def set_latency_and_packet_loss(self, latency, packet_loss_range):
        # 检查输入是否为范围（例如 "50-100ms"）
        if "-" in latency:
            min_latency, max_latency = latency.split("-")
            min_latency = min_latency.strip()
            max_latency = max_latency.strip().replace("ms", "")
            jitter = int(max_latency) - int(min_latency)
            latency = min_latency
        else:
            # 如果不是范围，只有一个值
            latency = latency.replace("ms", "").strip()
            jitter = None

        # 检查丢包率是否为范围（例如 "30-60"）
        if "-" in packet_loss_range:
            min_packet_loss, max_packet_loss = packet_loss_range.split("-")
            min_packet_loss = int(min_packet_loss.strip().replace("%", ""))
            max_packet_loss = int(max_packet_loss.strip().replace("%", ""))
            average_packet_loss = (min_packet_loss + max_packet_loss) / 2
            packet_loss_jitter = max_packet_loss - average_packet_loss
        else:
            # 如果不是范围，只有一个值
            average_packet_loss = int(packet_loss_range.strip().replace("%", ""))
            packet_loss_jitter = None

        # 在受限流量类上设置 netem 规则
        if jitter is None and packet_loss_jitter is None:
            command = f"tc qdisc add dev {self.interface} parent 1:11 handle 20: netem delay {latency}ms loss {average_packet_loss}%"
        elif jitter is not None and packet_loss_jitter is None:
            command = f"tc qdisc add dev {self.interface} parent 1:11 handle 20: netem delay {latency}ms {jitter}ms loss {average_packet_loss}%"
        elif jitter is None and packet_loss_jitter is not None:
            command = f"tc qdisc add dev {self.interface} parent 1:11 handle 20: netem delay {latency}ms loss {average_packet_loss}% {packet_loss_jitter}%"
        else:
            command = f"tc qdisc add dev {self.interface} parent 1:11 handle 20: netem delay {latency}ms {jitter}ms loss {average_packet_loss}% {packet_loss_jitter}%"
        self._execute(command)
    # 设置带宽
    def set_bandwidth(self, bandwidth, unrestricted_ports):
        assert 'up' in bandwidth, "'up'带宽未指定."
        assert 'down' in bandwidth, "'down'带宽未指定."

        command = f"tc qdisc add dev {self.interface} root handle 1: htb default 11"
        self._execute(command)

        # 添加无限制流量的类，并添加一个没有延迟和丢包的 netem 规则
        command = f"tc class add dev {self.interface} parent 1: classid 1:10 htb rate 5000mbit"
        self._execute(command)
        command = f"tc qdisc add dev {self.interface} parent 1:10 handle 10: netem delay 0ms loss 0%"
        self._execute(command)

        # 添加受限流量的类
        command = f"tc class add dev {self.interface} parent 1: classid 1:11 htb rate {bandwidth['down']}"
        self._execute(command)

        # 添加过滤器，将流量定向到相应的类。在这种情况下，指定端口的流量不受限制
        for port in unrestricted_ports:
            # 处理下行流量
            command = f"tc filter add dev {self.interface} protocol ip parent 1:0 prio 1 u32 match ip dport {port} 0xffff flowid 1:10"
            self._execute(command)
            # 处理上行流量
            command = f"tc filter add dev {self.interface} protocol ip parent 1:0 prio 1 u32 match ip sport {port} 0xffff flowid 1:10"
            self._execute(command)

        command = f"tc filter add dev {self.interface} protocol ip parent 1:0 prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:11"
        self._execute(command)
    # 设置最大传输单元（MTU）
    def set_mtu(self, mtu):
        command = f"ip link set dev {self.interface} mtu {mtu}"
        self._execute(command)


def main():
    # 创建一个TrafficControl对象，指定网络接口
    tc = TrafficControl('eth0')

    # 定义一个配置，设置带宽，延迟，MTU和丢包率
    config = {
        'bandwidth': {'up': '10mbit', 'down': '5mbit'},
        'latency': '50-100ms',
        'mtu': 1200,
        'packet_loss': '30-60%',
        'unrestricted_ports': [9007]  # SSH and HTTP
    }

    # 将配置应用到TrafficControl对象
    tc.configure(config)

    # 打印当前的网络状态
    print(tc._execute('tc qdisc show dev eth0'))
    print(tc._execute('ip link show dev eth0'))


if __name__ == "__main__":
    main()