import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_base.gnp_private_driver import GnpPrivateDriver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


'''
2020-08-21 Remove following test cases and labeling [M] to relevant Jama testcases due to:
1. It's not legal behavior to factory reset without sign out Teams account
2. It's complex if we would like to add sign out logic before sign in

@pytest.mark.feat_teams_app_settings_with_destroy_pairing
class TestFeatTeamsAppSettingsWithDestroyPairing(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.gnp_ins = GnpPrivateDriver()
        self.pcos_ins = init_apollo_pcos_driver()
        self.tc_jose_api_ins = JoseApiDriver(test_device="TC")

    def common_goto_general_page(self):
        # Factory reset TC and VB
        self.gnp_ins.gnp_write(self.tc_pid, "01", "13", "11", ["00"])
        self.gnp_ins.gnp_write(self.vb_pid, "01", "13", "11", ["00"])
        time.sleep(5)
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.pcos_ins.wait_device_pid_ready(self.vb_vid, 90, self.vb_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        """
        Hank has resolved the issue in latest version of Apollo Nico, so we don't need to disable the build-in keyboard manually.
        # Need to close build-in keyboard to use nico keyboard
        vb_ime_list = self.vb_cmd_driver.exec_adb_shell_cmd("ime list -s").split("\n")[0:-1]
        tc_ime_list = self.tc_cmd_driver.exec_adb_shell_cmd("ime list -s").split("\n")[0:-1]
        for ime in vb_ime_list:
            self.vb_cmd_driver.exec_adb_shell_cmd(f"ime disable {ime}")
        for ime in tc_ime_list:
            self.tc_cmd_driver.exec_adb_shell_cmd(f"ime disable {ime}")
        """
        # pair TC and VB from TC via JoseApiExample APP
        self.tc_jose_api_ins.pair_active_device(self.tc_pair_udid)
        # Set VaaS as Teams and Launch Teams app
        self.tc_jose_api_ins.vaas_settings_set_provider_teams()
        self.tc_jose_api_ins.launch_vaas_services()
        # Sign in Teams account in TC and VB
        self.vb_teams_room_ins.login()
        self.tc_teams_room_ins.login()
        # Verify DUT settings transferred to Touch Console Settings page.
        self.vb_teams_room_ins.check_sp_status("paired")
        # Go to Jabra Meeting general page in TC
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()

    @jama_tc(Gan_TC_ESW_43972,Gan_TC_ESW_43973)
    def test_teams_pair_unpair(self):
        self.common_goto_general_page()
        self.tc_jabra_meeting_driver.general_page().unpair_vaas()
        # Verify DUT and Touch console unpaired successfully and Touch Console gets signed out. Verify the more option displayed back in DUT.
        self.tc_teams_room_ins.check_sp_status("vaas_ready")
        self.vb_teams_room_ins.check_sp_status("home_ready")

    @jama_tc(Gan_TC_ESW_43974)
    def test_teams_sign_out(self):
        self.common_goto_general_page()
        self.tc_jabra_meeting_driver.general_page().sign_out_teams_account()
        # 1. Verify that user gets a visual indicator that user is getting signed out of the DUT Teams App. 2. Verify user gets signed out and navigate back sign in page
        self.tc_teams_room_ins.check_sp_status("vaas_ready")
        self.vb_teams_room_ins.check_sp_status("home_ready")
'''


@pytest.mark.feat_teams_app_settings_without_destroy_pairing
@pytest.mark.usefixtures("back_to_home")
class TestFeatTeamsAppSettingsWithoutDestroyPairing(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)

    @jama_tc(Gan_TC_ESW_43975, Fif_TC_ESW_109952)
    def test_about_option(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_app_settings()
        self.tc_teams_room_ins.handle_app_settings(function="check_settings_ui")
        teams_version = self.tc_cmd_driver.exec_adb_shell_cmd("pm dump com.microsoft.skype.teams.ipphone | grep versionName").split("=")[1]
        param = {"teams_version": teams_version}
        self.tc_teams_room_ins.handle_app_settings(function="check_about_ui", param=param)

    @jama_tc(Gan_TC_ESW_43976, Fif_TC_ESW_109953)
    def test_report_an_issue(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.handle_app_settings(function="check_report_issue_ui")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43977, Fif_TC_ESW_109954)
    def test_navigate_to_device_settings(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_app_settings()
        self.tc_teams_room_ins.handle_app_settings(function="check_settings_ui")
        self.tc_teams_room_ins.handle_app_settings(function="navigate_to_device_settings_and_back")
        self.tc_teams_room_ins.handle_app_settings(function="check_settings_ui")

    @jama_tc(Gan_TC_ESW_43978, Fif_TC_ESW_109955)
    def test_pairing_option(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_device_pairing_page()

    @pytest.mark.skip(reason='[GAN-21162] [MS_cert][TC/VB]Missing "Calling" menu in Teams Admin -> Access settings')
    @jama_tc(Gan_TC_ESW_43979, Fif_TC_ESW_110121)
    def test_calling_option(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_service_provider()
        self.tc_jabra_meeting_driver.general_page().open_teams_access_settings()
        self.tc_jabra_meeting_driver.general_page().check_teams_access_settings_ui()
