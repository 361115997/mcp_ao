import pytest, time, os
from apollo_gn_android.driver import GnAndroidDriver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_jabra.vb_jabra_meeting_driver.driver import VBJabraMeeting
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_device_user_settings
class TestFeatTeamsConsoleUserSettings(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.vb_jabra_meeting_driver = VBJabraMeeting()
        self.pcos_ins = init_apollo_pcos_driver()
        self.tc_gn_android = GnAndroidDriver(Base().tc_udid)
        self.vb_gn_android = GnAndroidDriver(Base().vb_udid)

    @jama_tc(Gan_TC_ESW_44034, Fif_TC_ESW_110020)
    def test_check_system_info_in_tc(self, teams_start_tc_jabra_meeting_setting, get_vb_info, get_tc_info):
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.home_page().goto_about_page()
        time.sleep(3)
        self.tc_jabra_meeting_driver.about_page().check_general_tab_ui(get_vb_info, get_tc_info)

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44035, Fif_TC_ESW_110021)
    def test_reboot_device_in_device_settings(self, teams_start_tc_jabra_meeting_setting):
        self.tc_jabra_meeting_driver.home_page().goto_restart()
        self.tc_jabra_meeting_driver.restart_page().check_device_restart_success()
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.pcos_ins.wait_device_pid_ready(self.vb_vid, 90, self.vb_pid)
        self.vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.tc_teams_room_ins.check_sp_status("home_ready")
        self.vb_teams_room_ins.check_sp_status("paired")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44038, Fif_TC_ESW_110024)
    def test_change_screensaver_timeout_in_tc(self, teams_start_tc_jabra_meeting_setting, resets_the_screen_timeout):
        # set device screen off timeout as 30s
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_video_page()
        self.tc_jabra_meeting_driver.video_page().goto_monitor()
        self.tc_jabra_meeting_driver.video_page().set_standby_interval("30")

        # Wait 10s, Check if the screen is on standby
        time.sleep(40)
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep InteractiveModeEnabled""")
        assert "mHalInteractiveModeEnabled=false" in rst

        # wait some seconds for syncing settings to VB
        time.sleep(6)
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep InteractiveModeEnabled""")
        assert "mHalInteractiveModeEnabled=false" in rst

    @jama_tc(Gan_TC_ESW_44810, Fif_TC_ESW_110025)
    def test_have_access_to_app_settings_and_device_settings_without_requiring_password(self, teams_start_tc_jabra_meeting_setting, resets_the_screen_timeout):
        # 1. Go to Admin
        self.tc_jabra_meeting_driver.home_page().goto_admin_page()

        # 2. Log in with invalid account
        self.tc_jabra_meeting_driver.admin_page().check_admin_login_failed()

        # 3.Log in with valid account
        self.tc_jabra_meeting_driver.admin_page().check_admin_login_success()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44824, Gan_TC_ESW_44811, Fif_TC_ESW_110026, Fif_TC_ESW_110026)
    def test_settings_are_on_sync_between_vb_and_tc(self, teams_start_tc_jabra_meeting_setting, restore_tc_default_settings, restore_vb_default_settings):
        # Turn on "High contrast mode"
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        time.sleep(2)
        self.tc_jabra_meeting_driver.accessibility_page().turn_on_high_contrast_mode()
        time.sleep(2)
        # Check the UI of all options sync_between_vb_and_tc
        self.tc_gn_android.android_setting().check_on_high_contrast_mode()
        self.vb_gn_android.android_setting().check_on_high_contrast_mode()

        # Go to admin, and reboot both TC&VB
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_system_reset()
        self.tc_jabra_meeting_driver.general_page().click_connected_devices_restart()
        self.tc_jabra_meeting_driver.general_page().click_ok_button()

        # Wait TC&VB ready
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.pcos_ins.wait_device_pid_ready(self.vb_vid, 90, self.vb_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)

        # Verify FoR DUT and Touch console both reboots and lands on connected state after reboot
        time.sleep(120)
        self.vb_teams_room_ins.check_sp_status("paired")

        # Go to Jabra meeting setting network settings
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()

        # Set TC as static ip
        self.tc_jabra_meeting_driver.network_page().goto_information_tc()
        self.tc_jabra_meeting_driver.network_page().goto_ip_configure_page()
        env_value = os.environ.get("env")
        if env_value == "a416":
            self.tc_jabra_meeting_driver.network_page().set_ip_address_static("10.101.60.228", "255.255.255.0", "10.101.60.1", "8.8.8.8", "192.168.140.5")
        else:
            self.tc_jabra_meeting_driver.network_page().set_ip_address_static("10.86.212.228", "255.255.255.0", "10.86.212.1", "10.86.214.12", "192.168.140.5")

        # Go to VB network page, check ip address type not change
        self.tc_jabra_meeting_driver.admin_page().goto_system_page()
        time.sleep(2)
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()
        self.tc_jabra_meeting_driver.network_page().goto_information_vb()
        time.sleep(2)
        self.tc_jabra_meeting_driver.network_page().expand_ip_configure_page()
        self.tc_jabra_meeting_driver.network_page().check_ip_address_type_dhcp()

        # Set TC as dhcp ip
        self.tc_jabra_meeting_driver.admin_page().goto_system_page()
        time.sleep(2)
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()
        self.tc_jabra_meeting_driver.network_page().goto_information_tc()
        time.sleep(2)
        self.tc_jabra_meeting_driver.network_page().goto_ip_configure_page()
        self.tc_jabra_meeting_driver.network_page().set_ip_address_dhcp()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44813, Fif_TC_ESW_110027)
    def test_device_based_on_android_oreo_or_higher(self):
        # 1 Check the device operating system.   adb shell getprop ro.build.version.release
        version = int(self.tc_cmd_driver.exec_adb_shell_cmd("getprop ro.build.version.release"))
        assert version > 8
