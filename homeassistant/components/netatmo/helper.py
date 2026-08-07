"""Helper for Netatmo integration."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from pyatmo.modules import BNAB, BNAS, BNMS, Module
from pyatmo.modules.device_types import DeviceType as NetatmoDeviceType


def device_type_to_str(device_type: NetatmoDeviceType) -> str:
    """Convert a device type to a string.

    Used to generate backwards compatible unique ids.
    """
    return f"{type(device_type).__name__}.{device_type}"


# Three pyatmo labels for the same BTicino MyHome BUS shutter hardware. These
# are the only shutters whose capabilities vary per actor and therefore have
# to be derived from what the actor reports about itself.
_BTICINO_MHS1_SHUTTERS = (BNAS, BNAB, BNMS)


def shutter_supports_position(shutter: Module) -> bool:
    """Return True if a shutter module can be moved to an exact position.

    A BTicino MyHome Server 1 actor reporting a target position step of 100
    can only be opened, closed and stopped. All other shutter types are
    treated as fully positionable.
    """
    if not isinstance(shutter, _BTICINO_MHS1_SHUTTERS):
        return True
    step: int | None = getattr(shutter, "target_position__step", None)
    return step is None or step < 100


def shutter_reports_current_position(shutter: Module) -> bool:
    """Return True if the shutter module reports a meaningful current position.

    A BTicino MyHome Server 1 actor that cannot be moved to an exact
    position mirrors the last commanded target position (101 = never
    instructed) instead of a real read-back. All other shutter types are
    trusted to report a real position.
    """
    if not isinstance(shutter, _BTICINO_MHS1_SHUTTERS):
        return True
    return shutter_supports_position(shutter)


def shutter_rejects_preferred_position(shutter: Module) -> bool:
    """Return True if the shutter module rejects moving to a preferred position.

    BTicino MyHome Server 1 actors reject this command (API error code 5)
    even when they support exact positioning; their presets are exposed as
    a separate actor issuing an ordinary percentage move.
    """
    return isinstance(shutter, _BTICINO_MHS1_SHUTTERS)


@dataclass
class NetatmoArea:
    """Class for keeping track of an area."""

    area_name: str
    lat_ne: float
    lon_ne: float
    lat_sw: float
    lon_sw: float
    mode: str
    show_on_map: bool
    uuid: UUID = field(default_factory=uuid4)
