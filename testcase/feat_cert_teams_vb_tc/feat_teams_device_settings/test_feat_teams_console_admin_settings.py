import random
import re

import pytest, time
from apollo_gn_android.driver import GnAndroidDriver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_web.web_gandalf_webui_driver import GandalfWebuiDriver

from apollo_jabra.jabrameeting_web_base import JabraMeetingWebBase
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_admin_settings
class TestFeatTeamsConsoleAdminSettings(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.tc_jabra_meeting_web_driver = GandalfWebuiDriver()
        self.pcos_ins = init_apollo_pcos_driver()
        self.gn_android = GnAndroidDriver(Base().tc_udid)

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting", "reset_password", "turn_on_web_console_by_default")
    @jama_tc(Gan_TC_ESW_44815, Gan_TC_ESW_44816, Gan_TC_ESW_44817, Gan_TC_ESW_44041, Gan_TC_ESW_44044, Gan_TC_ESW_44045, Gan_TC_ESW_44051, Fif_TC_ESW_110045, Fif_TC_ESW_110046, Fif_TC_ESW_110047, Fif_TC_ESW_110030, Fif_TC_ESW_110033, Fif_TC_ESW_110040)
    def test_tc_admin_settings(self):
        self.tc_cmd_driver.exec_adb_cmd("logcat -c") # Execute the logcat -c to make query fastly

        # 1 Go to Device Settings page
        # The Device Settings page is shown
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_account_page()

        # 2 Check account page UI
        self.tc_jabra_meeting_driver.account_page().check_account_page()

        # 3 turn off/on web console
        self.tc_jabra_meeting_driver.account_page().turn_off_web_console()
        self.tc_jabra_meeting_driver.account_page().turn_on_web_console()

        # 5 Change password
        self.tc_jabra_meeting_driver.account_page().click_change_password()
        self.tc_jabra_meeting_driver.account_page().change_invalid_password()
        self.tc_jabra_meeting_driver.account_page().click_change_password()
        password = f"Test!{random.randint(100, 999)}"
        self.tc_jabra_meeting_driver.account_page().change_valid_password(password)
        self.tc_jabra_meeting_driver.admin_page().close_admin_page()
        self.tc_jabra_meeting_driver.home_page().verify_new_password(password)

        # 6 Enable Bluetooth
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()
        self.tc_jabra_meeting_driver.network_page().goto_bluetooth()
        self.tc_jabra_meeting_driver.network_page().set_proximity_join("off")
        self.tc_jabra_meeting_driver.network_page().set_proximity_join("on")

        # 7 sign out admin account
        self.tc_jabra_meeting_driver.home_page().goto_about_page()

        # 8 check about page
        self.tc_jabra_meeting_driver.about_page().check_about_menu()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.flaky(reruns=1, reruns_delay=30)
    @jama_tc(Gan_TC_ESW_44046, Fif_TC_ESW_110035)
    def test_tc_set_language(self, teams_start_tc_jabra_meeting_setting, set_language_english):
        """
        Test Scenario
        1. Go to Admin->General->Region and Language
        2. Click the dropdown list of language,check if all supported language are shown
        3. Check the language has changed
        4. Change language back to English and check language has changed
        """
        # 1. Go to Admin->General->Region and Language
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_region_and_language()

        # 2 Click the dropdown list of language,check if all supported language are shown
        self.tc_jabra_meeting_driver.general_page().set_language_danish()
        time.sleep(15)  # Wait for language change reboot teams ready

        # 3 Check the language has changed
        current_language = self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.locale").strip()
        assert current_language == "da", "check_language_danish fail"

        # 4 Change language back to English and check language has changed
        self.tc_jabra_meeting_driver.general_page().set_language_english()
        time.sleep(15)  # Wait for language change reboot teams ready
        current_language = self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.locale").strip()
        assert current_language == "en-US", "check_language_english fail"

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.flaky(reruns=1, reruns_delay=30)
    @jama_tc(Gan_TC_ESW_44048, Fif_TC_ESW_110037)
    def test_tc_set_timezone(self, teams_start_tc_jabra_meeting_setting):
        """
        Test Scenario
        1. Go to Admin->General->Region and Language
        2. Choose any one time zone and check time zone has changed
        """
        # 1. Go to Admin->General->Region and Language
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_region_and_language()

        # 2 Choose any one time zone and check time zone has changed
        self.tc_jabra_meeting_driver.general_page().set_timezone_losangeles()
        assert self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.timezone").strip() == "America/Los_Angeles", "check_timezone_losangeles fail"
        self.tc_jabra_meeting_driver.general_page().set_timezone_london()
        assert self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.timezone").strip() == "Europe/London", "check_timezone_london fail"

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.flaky(reruns=1, reruns_delay=30)
    @jama_tc(Gan_TC_ESW_44047, Fif_TC_ESW_110036)
    def test_tc_set_time_format(self, teams_start_tc_jabra_meeting_setting):
        """
        Test Scenario
        1. Go to Admin->General->Region and Language
        2. Turn on 24-hour time format
        3. Turn off 24-hour time format
        """
        # 1. Go to Admin->General->Region and Language
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_region_and_language()

        # 2. Turn on 24-hour time format
        self.tc_jabra_meeting_driver.general_page().set_timeformat_24h()
        time.sleep(3)
        assert self.tc_cmd_driver.exec_adb_shell_cmd("settings get system time_12_24").strip() == "24", "check_timeformat_24h fail"

        # 3. Turn off 24-hour time format
        self.tc_jabra_meeting_driver.general_page().set_timeformat_12h()
        time.sleep(3)
        assert self.tc_cmd_driver.exec_adb_shell_cmd("settings get system time_12_24").strip() == "12", "check_timeformat_12h fail"

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44818, Gan_TC_ESW_44819, Fif_TC_ESW_110048, Fif_TC_ESW_110049)
    def test_verify_intent_for_teams_admin_settings_access(self, teams_start_tc_jabra_meeting_setting):
        self.tc_cmd_driver.exec_adb_shell_cmd("logcat -c")
        # Go to Admin->General->open teams access setting
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_service_provider()
        self.tc_jabra_meeting_driver.general_page().open_teams_access_settings()
        time.sleep(10)

        # Verify the intent: Intent Action: android.intent.action.view Intent Data:msteams:
        # //adminsettings Extra Info: settingsLoopbackCorrelationId
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep adminsettings | tail -1")
        assert "act=android.intent.action.VIEW dat=msteams://adminsettings" in rst
        assert "flg=0x10000000 cmp=com.microsoft.skype.teams.ipphone/com.microsoft.skype.teams.views.activities.SplashActivity (has extras)} from uid" in rst
        assert re.search(r"uid \d{5}", rst)

        # Check for pairing in Teams admin settings.
        self.tc_teams_room_ins.admin_setting_page().click_devices()
        self.tc_teams_room_ins.admin_setting_page().check_devices_page()
        self.tc_teams_room_ins.admin_setting_page().click_console_pairing()
        self.tc_teams_room_ins.admin_setting_page().check_console_pairing_page()

    @jama_tc(Gan_TC_ESW_44051, Fif_TC_ESW_110040)
    # 6.4 [Admin Settings]Teams app preinstalled on the DUT
    def test_verify_teams_app_preinstalled(self):
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("pm list packages")
        assert "com.microsoft.skype.teams.ipphone" in rst

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    # 6.4 [Web UI] DUT User to verify the https support for Web UI
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting", "turn_on_web_console_by_default")
    @jama_tc(Gan_TC_ESW_44821, Fif_TC_ESW_110051)
    def test_tc_verify_https_support_for_web_ui(self):
        # verify_https_support_for_web_ui
        web_driver = JabraMeetingWebBase(Base().tc_udid)
        web_driver.open_jabrameeting_web()
        self.tc_jabra_meeting_web_driver.login()

    @jama_tc(Gan_TC_ESW_44053, Fif_TC_ESW_110042)
    def test_tc_read_network_setting(self, teams_start_tc_jabra_meeting_setting):
        # Go to network setting page
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()
        self.tc_jabra_meeting_driver.admin_page().goto_audio_page()
        self.tc_jabra_meeting_driver.admin_page().goto_network_page()

        self.tc_jabra_meeting_driver.network_page().goto_information_vb()

        # check IP and MAC address is show
        self.tc_jabra_meeting_driver.network_page().check_network_ipv4_data(self.vb_udid, "VB")

    # @jama_tc(Gan_TC_ESW_44042)
    # def test_reset_the_config_parameters_to_default(self, teams_start_tc_jabra_meeting_setting):
    #     # Turn on "High contrast mode"
    #     self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
    #     self.tc_jabra_meeting_driver.accessibility_page().turn_on_high_contrast_mode()
    #     time.sleep(3)
    #     self.gn_android.android_setting().check_on_high_contrast_mode()
    #
    #     # Go to general setting page
    #     self.tc_jabra_meeting_driver.home_page().goto_admin()
    #     self.tc_jabra_meeting_driver.admin_page().goto_general_page()
    #     self.tc_jabra_meeting_driver.general_page().goto_system_reset()
    #
    #     # Reset config parameters to default
    #     self.tc_jabra_meeting_driver.general_page().click_user_default_settings_reset()
    #     self.tc_jabra_meeting_driver.general_page().click_ok_button()
    #     self.tc_jabra_meeting_driver.general_page().click_done_button()
    #
    #     # Verify "High contrast mode" is off
    #     time.sleep(3)
    #     self.gn_android.android_setting().check_off_high_contrast_mode()
