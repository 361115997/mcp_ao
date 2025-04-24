import time

import pytest
from apollo_base.cmd_driver import CmdDriver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


# @pytest.mark.feat_teams_console_device_settings_after_qfil
# class TestFeatTeamsConsolePairingAfterQFil(Base):

#     def setup_class(self):
#         self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
#         self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
#         self.tc_jabra_meeting_driver = TCJabraMeeting()
#         self.tc_cmd_driver = CmdDriver(Base().tc_udid)

#     def teardown(self):
#         self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")

#     @jama_tc(Gan_TC_ESW_44823,Gan_TC_ESW_44827)
#     def test_unpair_device_then_repair(self, pair_tc_vb):
#         self.tc_teams_room_ins.open()
#         self.tc_teams_room_ins.login()
#         self.tc_teams_room_ins.check_sp_status("home_ready")
#         self.tc_teams_room_ins.goto_jabra_meeting()

#         # Unpair FoR and Touch console
#         self.tc_jabra_meeting_driver.home_page().goto_admin()
#         self.tc_jabra_meeting_driver.admin_page().goto_general_page()
#         self.tc_cmd_driver.exec_adb_shell_cmd("logcat -c")
#         self.tc_jabra_meeting_driver.general_page().unpair_vaas()
#         self.tc_teams_room_ins.check_sp_status("vaas_ready")

#         # Verify DUT user is able to unpair with touch console
#         # This intent is sent from the console Teams client to
#         # the console firmware. Intent action: com.microsoft.skype.teams.console.action
#         # Intent extras: key: correlationId, value: a unique GUID to identify
#         # the action intent key: actionName, value: unpair
#         rst = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT-TeamsUnpairIntentData | "
#                                                     "tail -2")
#         assert "actionName=unpair" in rst

#         # login and repair
#         self.tc_teams_room_ins.login()
#         self.tc_teams_room_ins.check_sp_status("home_ready")


@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_console_pairing
class TestFeatTeamsConsoleDeviceSettings(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)

    @jama_tc(Gan_TC_ESW_44828, Fif_TC_ESW_110059)
    @pytest.mark.skip(reason="The actions involving pairing and unpairing are not stable enough.")
    def test_pairing_settings_on_tc_during_network_outage(self, restore_tc_network_connect):
        # Disable network
        self.tc_cmd_driver.exec_adb_shell_cmd("logcat -c")
        disable_network = "ifconfig eth0 down"
        self.tc_cmd_driver.exec_adb_shell_cmd(disable_network)
        time.sleep(20)

        # Verify device does not have network.
        # This intent is sent from the console firmware to the console Teams client.
        # Intent action: com.microsoft.skype.teams.console.oem.action Intent extras: key: correlationId,
        # value: a unique GUID to identify the action intent key: actionName, value: pairingStatusUpdated
        # Key: pairingStatus, value: an enum value representing the pairing status, should be one of – paired, unpaired
        rst = self.tc_cmd_driver.exec_adb_shell_cmd('logcat -d | grep "JABRA_PARTNER_AGENT-TeamsPairingStatusUpdatedIntentData" | tail -1')
        assert " pairingStatus=inactive, actionName=pairingStatusUpdated" in rst
