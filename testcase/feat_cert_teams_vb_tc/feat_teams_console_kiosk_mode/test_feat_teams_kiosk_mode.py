import pytest, time
from apollo_base.cmd_driver import CmdDriver
from apollo_base.decorate import jama_tc
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver

from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.feat_teams_console_kiosk_mode
class TestFeatTeamsConsoleKioskMode(Base):
    """
    Two PCs needed, not suitable for current setup
    """

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pcos_ins = init_apollo_pcos_driver()

        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43856, Gan_TC_ESW_43857, Gan_TC_ESW_44797, Fif_TC_ESW_109836, Fif_TC_ESW_109837, Fif_TC_ESW_109838)
    def test_tc_teams_should_get_launched_after_power_up(self):
        self.tc_teams_room_ins.check_is_in_kiosk_mode()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43862, Gan_TC_ESW_43859, Fif_TC_ESW_109843, Fif_TC_ESW_109840)
    def test_tc_no_way_to_exit_kiosk_mode(self):
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 540 0 540 1600 1000")
        time.sleep(1)
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 540 1600 540 0 1000")
        time.sleep(1)
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 200 960 1600 960 1000")
        time.sleep(1)
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 1600 960 200 960 1000")
        time.sleep(5)
        self.tc_teams_room_ins.check_sp_status("home_ready")
