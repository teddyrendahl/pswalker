############
# Standard #
############

###############
# Third Party #
###############
import pytest
from ophyd.ophydobj import OphydObject

##########
# Module #
##########
from pswalker.examples import YAG, Mirror, Source, patch_yags

@pytest.fixture(scope='function')
def simple_two_bounce_system():
    """
    Simple system that consists of a source and two mirrors.
    """
    s = Source('test_source', 0, 0)
    m1 = Mirror('test_mirror_1', 0, 10, 0)
    m2 = Mirror('test_mirror_2', 5, 20, 0)
    return s, m1, m2

@pytest.fixture(scope='function')
def one_bounce_system():
    """
    Generic single bounce system consisting one mirror with a linear
    relationship with YAG centroid
    """
    mot = Mirror('mirror', 0, 50, 0)
    det = YAG('yag', 0, 60, pix=(500,500))
    det = patch_yags(det, mot)
    return mot, det


class FakePath(OphydObject):
    SUB_VALUE = "value"
    SUB_PTH_CHNG = SUB_VALUE
    _default_sub = SUB_PTH_CHNG

    def __init__(self, *devices):
        self.devices = sorted(devices, key=lambda d: d.read()["z"]["value"])
        super().__init__()

    def clear(self, *args, **kwargs):
        for device in self.devices:
            if device.blocking:
                device.set("OUT")

    # Looks dumb but I kind of need it because a Reader is subtly different
    # than an OphydObject
    def _run_subs(self, *args, sub_type=_default_sub, **kwargs):
        super()._run_subs(*args, sub_type=sub_type, **kwargs)

    def subscribe(self, *args, **kwargs):
        # Potential danger if we subscribe multiple times in a test
        for dev in self.devices:
            dev.subscribe(self._run_subs)
        super().subscribe(*args, **kwargs)

    @property
    def blocking_devices(self):
        return [d for d in self.devices if d.blocking]


@pytest.fixture(scope='function')
def fake_path_two_bounce():
    """
    pswalker-compatible lightpath.BeamPath with fake objects. Pretends to be
    the HOMS system.
    """
    
    p1h = YAG("p1h", 0, 0)
    feem1 = Mirror("feem1", 0, 10, 0)
    p2h = YAG("p2h", 0, 20)
    feem2 = Mirror("feem2", 0, 30, 0)
    p3h = YAG("p3h", 0, 40)
    hx2_pim = YAG("hx2_pim", 0, 50)
    um6_pim = YAG("um6_pim", 0, 60)
    dg3_pim = YAG("dg3_pim", 0, 70)

    yags = [p1h, p2h, hx2_pim, um6_pim, dg3_pim]
    p1h, p2h, hx2_pim, um6_pim, dg3_pim = patch_yags(yags, [feem1, feem2])
    
    path = FakePath(p1h, feem1, p2h, feem2, p3h, hx2_pim, um6_pim, dg3_pim)
    return path
