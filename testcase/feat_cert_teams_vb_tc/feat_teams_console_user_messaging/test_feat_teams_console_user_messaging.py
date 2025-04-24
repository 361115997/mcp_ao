import pytest, time
from apollo_base.cmd_driver import CmdDriver
from apollo_base.decorate import jama_tc
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_web.web_tac_driver import WebTacDriver

from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.feat_teams_console_user_messaging
class TestFeatTeamsConsoleUserMessaging(Base):
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pcos_ins = init_apollo_pcos_driver()
        self.web_tac_driver = WebTacDriver()
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)

    @jama_tc(Gan_TC_ESW_44066, Fif_TC_ESW_110071)
    def test_teams_should_provide_error_message_when_network_error(self, recovery_vb_network, recovery_tc_network):
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_no_internet()
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.tc_teams_room_ins.check_no_internet()

    @jama_tc(Gan_TC_ESW_44067, Fif_TC_ESW_110072)
    def test_teams_should_provide_error_message_after_crash(self, recovery_tc_teams, recovery_vb_teams):
        self.vb_teams_room_ins.open()
        self.tc_teams_room_ins.open()
        for _ in range(5):
            self.tc_cmd_driver.exec_adb_shell_cmd("am start -n com.microsoft.skype.teams.ipphone/com.microsoft.skype.teams.Launcher")
            self.tc_cmd_driver.exec_adb_shell_cmd("am crash com.microsoft.skype.teams.ipphone")
        self.tc_teams_room_ins.check_teams_crash()
        for i in range(5):
            self.vb_cmd_driver.exec_adb_shell_cmd("am start -n com.microsoft.skype.teams.ipphone/com.microsoft.skype.teams.Launcher")
            self.vb_cmd_driver.exec_adb_shell_cmd("am crash com.microsoft.skype.teams.ipphone")
        self.vb_teams_room_ins.check_teams_crash()
