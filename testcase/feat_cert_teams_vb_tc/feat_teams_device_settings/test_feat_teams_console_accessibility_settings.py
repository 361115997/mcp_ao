import pytest, time
from testcase.base import Base
from apollo_base.decorate import jama_tc
from apollo_gn_android.driver import GnAndroidDriver
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_accessibility_settings
class TestFeatTeamsConsoleAccessibilitySettings(Base):

    def setup_class(self):
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.gn_android = GnAndroidDriver(Base().tc_udid)

    @jama_tc(Gan_TC_ESW_44024, Gan_TC_ESW_44023, Fif_TC_ESW_110010, Fif_TC_ESW_110009)
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting")
    def test_tc_accessibility_settings_page_accessibility_setting_option(self):
        # 1 Click tab "accessibility_page";
        # The;Accessibility &gt;&gt;;Accessibility page is shown
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().check_active_page()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44025, Gan_TC_ESW_44027, Fif_TC_ESW_110011, Fif_TC_ESW_110014)
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting")
    def test_tc_accessibility_settings_page_text_size(self):
        # 1.Reboot TC
        # Click tab "accessibility_page";
        # The;Accessibility &gt;&gt;;Accessibility page is shown
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().check_active_page()

        # 2 Change the Text size slider with different values
        # Confirm the;Text size is updated.
        # Verify the setting;reflect on the device
        self.tc_jabra_meeting_driver.accessibility_page().set_text_size_largest()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_largest()

        # 3 Change the;Text size slider with min./max. setting&#39;s value.
        # Confirm the;Text size is updated.
        # Verify the setting;reflect on the device
        self.tc_jabra_meeting_driver.accessibility_page().set_text_size_small()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_small()

        # 4 Try to change the;Text size slider to values out of min./max. setting&#39;s value.
        # Confirm the;Text size;is not set.
        # Verify the setting;reflect on the device
        self.tc_jabra_meeting_driver.accessibility_page().set_text_size_outof_bar()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_small()

        # 5 Try to change the;Text size slider to values out of min./max. setting&#39;s value.
        # Confirm the;Text size;is not set.
        # Verify the setting;reflect on the device
        self.tc_jabra_meeting_driver.home_page().goto_about_page()
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().set_text_size_largest()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_largest()
        self.tc_jabra_meeting_driver.accessibility_page().reset_text_size()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_small()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44030, Gan_TC_ESW_44031, Gan_TC_ESW_44026, Fif_TC_ESW_110016, Fif_TC_ESW_110019, Fif_TC_ESW_110012)
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting")
    def test_tc_accessibility_settings_page_contrast_mode(self):
        # 1 Click tab "accessibility_page";
        # The;Accessibility &gt;&gt;;Accessibility page is shown
        self.tc_jabra_meeting_driver.home_page().goto_about_page()

        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().check_active_page()
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().check_active_page()

        # 2 Turn off "High contrast mode", check the UI of all options
        # The setting is saved with success
        # Verify High contrast mode reflect on the video
        time.sleep(2)
        self.tc_jabra_meeting_driver.accessibility_page().turn_off_high_contrast_mode()
        time.sleep(1.5)
        self.gn_android.android_setting().check_off_high_contrast_mode()

        # 3 Turn on "High contrast mode", check the UI of all options
        # The setting is saved with success
        # Verify High contrast mode reflect on the video
        self.tc_jabra_meeting_driver.accessibility_page().turn_on_high_contrast_mode()
        time.sleep(1.5)
        self.gn_android.android_setting().check_on_high_contrast_mode()
        time.sleep(1.5)
        self.tc_jabra_meeting_driver.accessibility_page().turn_off_high_contrast_mode()

    @jama_tc(Gan_TC_ESW_44028, Fif_TC_ESW_110017)
    @pytest.mark.usefixtures("teams_start_tc_jabra_meeting_setting")
    def test_tc_accessibility_settings_after_reboot(self, reboot_tc):
        # 1 Set the text size as default from adb command
        self.gn_android.android_setting().set_text_size_default()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_default()

        # 2 Set the text size as largest via jabra meeting
        self.tc_jabra_meeting_driver.home_page().goto_accessibility_page()
        self.tc_jabra_meeting_driver.accessibility_page().check_active_page()
        self.tc_jabra_meeting_driver.accessibility_page().set_text_size_largest()
        time.sleep(1.5)
        self.gn_android.android_setting().check_text_size_largest()

        # 3 Reboot the TC and check the text size via adb command
        reboot_tc()
        time.sleep(30)
        self.gn_android.android_setting().check_text_size_largest()

        # 4 Set the text size as default from adb command
        self.gn_android.android_setting().set_text_size_default()
