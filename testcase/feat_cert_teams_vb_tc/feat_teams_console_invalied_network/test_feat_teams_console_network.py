import pytest, time
from apollo_base.cmd_driver import CmdDriver
from apollo_base.decorate import jama_tc
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver

from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.feat_teams_console_invalid_network
class TestFeatTeamsConsoleNetwork:
    """
    Two PCs needed, not suitable for current setup
    """

    def setup_class(self):
        self.dut_name = Base().dut_name
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.audio_ins = AudioDriver()
        self.ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().get_sys_info["PC_AG_WIN"]["Teams"]["user"]
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.pc_ag_phone_number = Base().pc_ag_win["Teams"]["phone_number"]

    @pytest.mark.skip(reason="Need re login")
    @jama_tc(Gan_TC_ESW_44057, Fif_TC_ESW_110062)
    def test_sign_in_error_handling_during_network_outage(self, factory_reset_then_pair_tc_vb, recovery_tc_network, recovery_vb_network):
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.tc_teams_room_ins.check_no_internet()
        self.tc_teams_room_ins.login_without_register()
        self.tc_teams_room_ins.check_login_fail()
        self.tc_teams_room_ins.adb_utils.back()
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_no_internet()
        self.vb_teams_room_ins.login_without_register()
        self.vb_teams_room_ins.check_login_fail()
        self.vb_teams_room_ins.adb_utils.back()

    @jama_tc(Gan_TC_ESW_44058, Fif_TC_ESW_110063)
    def test_network_outage_when_user_is_on_home_screen(self, recovery_tc_network, recovery_vb_network):
        # Seems we don't need this step as we we put it on FWU_Teams setup
        # self.vb_teams_room_ins.login()
        # self.vb_teams_room_ins.check_sp_status("home_ready")
        # Seems we don't need this step as we we put it on FWU_Teams setup
        # self.tc_teams_room_ins.login()
        self.tc_teams_room_ins.check_sp_status("home_ready")
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_no_internet()
        time.sleep(120)
        self.tc_teams_room_ins.check_device_not_found()

    @jama_tc(Gan_TC_ESW_44060, Fif_TC_ESW_110065)
    def test_join_meeting_when_network_outage(self,recovery_tc_network,recovery_vb_network,tc_back,cancel_scheduled_meeting):
        self.ag_teams_ins.scheduled_meeting("Test", self.tc_teams_user)
        time.sleep(60)
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        time.sleep(60)
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.join_scheduled_meeting(check_joined=False)
        self.vb_teams_room_ins.check_meet_now_fail()

    @jama_tc(Gan_TC_ESW_44059, Fif_TC_ESW_110064)
    def test_make_call_when_network_outage(self, recovery_tc_network):
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.tc_teams_room_ins.check_no_internet()
        time.sleep(1)
        self.tc_teams_room_ins.initial_call(self.pc_ag_phone_number, check_status=False)
        self.tc_teams_room_ins.check_sp_status("home_ready")

    @jama_tc(Gan_TC_ESW_44061, Fif_TC_ESW_110066)
    def test_network_outage_during_a_call(self, recovery_vb_network, recovery_tc_network, recovery_vb_teams, cleanup_sp_call):
        self.tc_teams_room_ins.initial_call(self.pc_ag_phone_number)
        time.sleep(3)
        self.ag_teams_ins.accept_call()
        time.sleep(5)
        self.ag_teams_ins.check_call_status("active_unmute", self.tc_teams_user)
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_searching_network()
        self.vb_teams_room_ins.check_call_dropped()

    @jama_tc(Gan_TC_ESW_44062, Fif_TC_ESW_110067)
    def test_network_outage_during_meeting(self, recovery_vb_network, recovery_tc_network, recovery_vb_teams, cleanup_sp_meeting):
        self.ag_teams_ins.initial_meeting()
        self.ag_teams_ins.invite_people_into_meeting(self.tc_teams_user)
        time.sleep(2)
        self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.tc_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_searching_network()
        self.vb_teams_room_ins.check_call_dropped()

    @jama_tc(Gan_TC_ESW_44064, Fif_TC_ESW_110069)
    def test_network_outage_for_a_short_time_during_meeting(self, recovery_vb_network, recovery_tc_network, cleanup_sp_meeting):
        self.ag_teams_ins.initial_meeting()
        self.ag_teams_ins.invite_people_into_meeting(self.tc_teams_user)
        time.sleep(2)
        self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_searching_network()
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")
        time.sleep(5)
        self.vb_teams_room_ins.check_dut_camera_video_valid()

    @jama_tc(Gan_TC_ESW_44063, Fif_TC_ESW_110068)
    def test_network_outage_for_a_short_time_during_call(self, recovery_vb_network, recovery_tc_network, cleanup_sp_call):
        self.tc_teams_room_ins.initial_call(self.pc_ag_phone_number)
        self.ag_teams_ins.accept_call()
        time.sleep(2)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 down")
        self.vb_teams_room_ins.check_searching_network()
        self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")
        time.sleep(5)
        self.vb_teams_room_ins.check_dut_camera_video_valid()
