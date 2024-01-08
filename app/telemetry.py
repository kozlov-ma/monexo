from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


def defaultd_int():
    return defaultdict(int)


def defaultd_float():
    return defaultdict(float)


@dataclass
class TelemetryData:
    int_values: defaultdict[str, int] = field(default_factory=defaultd_int)
    float_values: defaultdict[str, float] = field(default_factory=defaultd_float)
    other_values: dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        msg = ["<b>Общая статистика бота:</b>"]
        for k, v in sorted(self.int_values.items(), key=lambda p: p[0]):
            msg.append(f"<b>{k}</b>: {v}")
        if self.int_values:
            msg.append('\n')
        for k, v in sorted(self.float_values.items(), key=lambda p: p[0]):
            msg.append(f"<b>{k}</b>: {v}")
        if self.float_values:
            msg.append('\n')
        for k, v in sorted(self.other_values.items(), key=lambda p: p[0]):
            msg.append(f"<b>{k}</b>: {v}")
        if self.other_values:
            msg.append('\n')

        return "\n".join(msg)
