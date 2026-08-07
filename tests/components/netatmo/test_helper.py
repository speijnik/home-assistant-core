"""The tests for Netatmo integration helpers."""

from pyatmo.modules import BNAS, NBO

from homeassistant.components.netatmo.helper import (
    shutter_rejects_preferred_position,
    shutter_reports_current_position,
    shutter_supports_position,
)


def _make_shutter(shutter_class: type, step: int | None) -> object:
    """Build a bare shutter instance with only target_position__step set.

    Bypasses __init__ (which needs a real Home/module payload) since these
    tests only care about the step-based/class-based capability checks.
    """
    shutter = shutter_class.__new__(shutter_class)
    shutter.target_position__step = step
    return shutter


def test_calibrated_bnas_supports_position_and_reports_it() -> None:
    """Test a calibrated BNAS shutter is treated as fully positionable.

    A calibrated BTicino shutter reporting as BNAS (e.g. an F401) must
    still be treated as reporting a genuine current position, even though
    an uncalibrated BNAS (e.g. F411) doesn't - a shutter that can be
    commanded to an arbitrary position has to report a real one back for
    that to be a coherent feature at all.
    """
    shutter = _make_shutter(BNAS, step=1)
    assert shutter_supports_position(shutter) is True
    assert shutter_reports_current_position(shutter) is True


def test_calibrated_bnas_still_rejects_preferred_position() -> None:
    """Test a calibrated BNAS shutter still rejects preferred position.

    Preset positions for BTicino shutters that do support exact
    positioning are implemented by a separate button/switch actor
    commanding an ordinary percentage move, not through this command.
    """
    shutter = _make_shutter(BNAS, step=1)
    assert shutter_rejects_preferred_position(shutter) is True


def test_uncalibrated_bnas_does_not_report_current_position() -> None:
    """Test an uncalibrated BNAS shutter doesn't report a real position.

    An uncalibrated BNAS (e.g. F411) can't be trusted to report a genuine
    current position - confirmed against real hardware.
    """
    shutter = _make_shutter(BNAS, step=100)
    assert shutter_supports_position(shutter) is False
    assert shutter_reports_current_position(shutter) is False
    assert shutter_rejects_preferred_position(shutter) is True


def test_bubendorff_keeps_its_pre_existing_behavior() -> None:
    """Test a Bubendorff shutter is unaffected by MyHome Server 1 checks.

    A Bubendorff shutter keeps its long-standing default behavior
    unconditionally - full exact-position support, a trusted current
    position, and preferred-position support - unaffected by the BTicino
    MyHome Server 1 step-based capability checks, even though it happens
    to report the same target position step as an uncalibrated MyHome
    Server 1 shutter.
    """
    shutter = _make_shutter(NBO, step=100)
    assert shutter_supports_position(shutter) is True
    assert shutter_reports_current_position(shutter) is True
    assert shutter_rejects_preferred_position(shutter) is False
