import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_web.web_gandalf_teams_driver import WebGandalfTeamsDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_base.gnp_private_driver import GnpPrivateDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *

"""
2020-08-21 Remove following test cases and labeling [M] to relevant Jama testcases due to:
1. It's not legal behavior to factory reset without sign out Teams account
2. It's complex if we would like to add sign out logic before sign in

@pytest.mark.usefixtures("exit_chrome")
@pytest.mark.feat_teams_sign_in_sign_out_after_qfil
class TestTeamsSignInSignOutAfterQfil(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.web_ins = WebGandalfTeamsDriver()
        self.tc_jabra_meeting_driver = TCJabraMeeting()

    def pair_device_and_set_vaas_teams(self):
        tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        tc_cmd_driver = CmdDriver(Base().tc_udid)
        vb_cmd_driver = CmdDriver(Base().vb_udid)
        tc_jose_api_ins = JoseApiDriver(test_device="TC")
        gnp_ins = GnpPrivateDriver()
        pcos_ins = init_apollo_pcos_driver()

        # Factory reset TC and VB
        gnp_ins.gnp_write(Base().tc_pid, "01", "13", "11", ["00"])
        gnp_ins.gnp_write(Base().vb_pid, "01", "13", "11", ["00"])
        time.sleep(5)
        pcos_ins.wait_device_pid_ready(Base().tc_vid, 90, Base().tc_pid)
        pcos_ins.wait_device_pid_ready(Base().vb_vid, 90, Base().vb_pid)
        tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        # pair TC and VB from TC via JoseApiExample APP
        tc_jose_api_ins.pair_active_device(Base().tc_pair_udid)
        # Set VaaS as Teams and Launch Teams app
        tc_jose_api_ins.vaas_settings_set_provider_teams()
        tc_jose_api_ins.launch_vaas_services()
        tc_teams_room_ins.check_sp_status("vaas_ready")
        vb_teams_room_ins.check_sp_status("vaas_ready")

    @jama_tc(Gan_TC_ESW_43864)
    def test_sign_in_from_web(self):
        self.pair_device_and_set_vaas_teams()
        # Login VB from web
        vb_login_code = self.vb_teams_room_ins.get_web_login_code()
        self.web_ins.login_teams(vb_login_code)
        time.sleep(60)
        self.vb_teams_room_ins.check_sp_status("home_ready")
        # Login TC from web
        tc_login_code = self.tc_teams_room_ins.get_web_login_code()
        self.web_ins.login_teams(tc_login_code)
        time.sleep(60)
        self.tc_teams_room_ins.check_sp_status("home_ready")
        # Wait for TC and VB to be paired
        self.vb_teams_room_ins.check_sp_status("paired")
"""


@pytest.mark.feat_teams_sign_in_sign_out
class TestTeamsSignInSignOut(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.pcos_ins = init_apollo_pcos_driver()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43868, Fif_TC_ESW_109849)
    def test_auto_sign_in_after_reboot(self):
        self.tc_teams_room_ins.open()
        # 1. Go to Admin->General->System reset
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_system_reset()
        self.tc_jabra_meeting_driver.general_page().click_connected_devices_restart()
        self.tc_jabra_meeting_driver.general_page().click_ok_button()
        time.sleep(10)
        self.pcos_ins.wait_device_pid_ready(Base().tc_vid, 120, Base().tc_pid)
        self.pcos_ins.wait_device_pid_ready(Base().vb_vid, 120, Base().vb_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 100)
        self.vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 100)
        self.tc_teams_room_ins.check_sp_status("home_ready")
        self.vb_teams_room_ins.check_sp_status("paired")
