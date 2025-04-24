import pytest, pytz, time
from datetime import datetime, timedelta
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_home_screen
class TestFeatTeamsHomeScreen(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pc_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_jose_ins = JoseApiDriver("TC")
        self.vb_jose_ins = JoseApiDriver("VB")
        self.pc_teams_display_name = Base().pc_ag_win["Teams"]["display_name"]
        self.tc_teams_user = Base().tc_teams["user"]
        self.tc_timezone = self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.timezone").strip()
        self.tc_teams_room_ins.cleanup_sp_meeting()
        self.pc_teams_ins.cleanup_sp_meeting()

    @jama_tc(Gan_TC_ESW_43884, Fif_TC_ESW_109866)
    def test_home_screen(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.check_home_screen()

    @jama_tc(Gan_TC_ESW_43889, Fif_TC_ESW_109870)
    def test_more_options(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.check_more_options()

    @jama_tc(Gan_TC_ESW_43887, Fif_TC_ESW_109868)
    def test_display_current_time(self):
        # Get current time format on TC
        tc_time_format = self.tc_cmd_driver.exec_adb_shell_cmd("settings get system time_12_24").strip()
        # Get current time on TC
        self.tc_teams_room_ins.open()
        tc_display_time = self.tc_teams_room_ins.get_dispaly_time()
        # Get current time on VB
        self.vb_teams_room_ins.open()
        vb_display_time = self.vb_teams_room_ins.get_dispaly_time()

        # Get standard time of current time zone
        if tc_time_format == "12":
            standard_time = datetime.now(pytz.timezone(self.tc_timezone)).strftime("%I:%M %p")
            standard_time_minus_one = (datetime.now(pytz.timezone(self.tc_timezone)) - timedelta(minutes=1)).strftime("%I:%M %p")
        else:
            standard_time = datetime.now(pytz.timezone(self.tc_timezone)).strftime("%H:%M")
            standard_time_minus_one = (datetime.now(pytz.timezone(self.tc_timezone)) - timedelta(minutes=1)).strftime("%I:%M")

        assert tc_display_time in standard_time or tc_display_time in standard_time_minus_one, f"TC time is not correct. display_time: {tc_display_time}, standard_time: {standard_time}, standard_time_minus_one: {standard_time_minus_one}"
        assert vb_display_time in standard_time or vb_display_time in standard_time_minus_one, f"VB time is not correct. display_time: {vb_display_time}, standard_time: {standard_time}, standard_time_minus_one: {standard_time_minus_one}"

    @jama_tc(Gan_TC_ESW_43891, Fif_TC_ESW_109871)
    def test_dpi_value(self):
        # Get DPI value on TC
        tc_density = self.tc_cmd_driver.exec_adb_shell_cmd("wm density").strip()
        assert tc_density == "Physical density: 240", f"TC DPI is not correct. Expected: 240, Actual: {tc_density}"

        # Get DPI value on VB
        resolution = self.vb_cmd_driver.exec_adb_shell_cmd("wm size").strip()
        vb_density = self.vb_cmd_driver.exec_adb_shell_cmd("wm density").strip()
        if "1920x1080" in resolution:
            assert "Override density: 160" in vb_density, f"Override density incorrect. Expected: 160, Actual: {vb_density}"
        elif "3840x2160" in resolution:
            assert "Override density: 320" in vb_density, f"Override density incorrect. Expected: 320, Actual: {vb_density}"
        else:
            raise ValueError(f"Resolution: {resolution} is not configured.")

    @pytest.mark.usefixtures("back_to_home")
    @pytest.mark.usefixtures("cancel_all_scheduled_meetings")
    @jama_tc(Gan_TC_ESW_43892, Gan_TC_ESW_43893, Fif_TC_ESW_109872, Fif_TC_ESW_109873)
    def test_meeting_time_with_different_format(self):
        # Set time format to 24h
        self.tc_jose_ins.set_timeformat_24h()
        # Schedule a meeting with DUT from TDC after the next 5 hours
        start_time = (datetime.now() + timedelta(hours=1)).strftime("%I:%M %p")
        end_time = (datetime.now() + timedelta(hours=2)).strftime("%I:%M %p")
        self.pc_teams_ins.scheduled_meeting(subject="Upcoming meeting", esp_user=self.tc_teams_user, start_time=start_time, end_time=end_time)
        time.sleep(5)
        # Get scheduled meeting time on TC
        self.tc_teams_room_ins.open()
        scheduled_time = self.tc_teams_room_ins.get_scheduled_meeting_date(subject="Upcoming meeting")
        assert "AM" not in scheduled_time and "PM" not in scheduled_time, f"TC sceduled meeting display format is not correct."

        # Set time format to 12h
        self.tc_jose_ins.set_timeformat_12h()
        # Get scheduled meeting time on TC
        self.tc_teams_room_ins.open()
        scheduled_time = self.tc_teams_room_ins.get_scheduled_meeting_date(subject="Upcoming meeting")
        assert "AM" in scheduled_time or "PM" in scheduled_time, f"TC sceduled meeting display format is not correct."

    @pytest.mark.usefixtures("cancel_all_scheduled_meetings")
    @jama_tc(Gan_TC_ESW_43882, Gan_TC_ESW_43883, Fif_TC_ESW_109864, Fif_TC_ESW_109865)
    def test_display_meeting_info(self):
        # Schedule a current meeting
        start_time1 = (datetime.now() - timedelta(minutes=15)).strftime("%I:%M %p")
        end_time1 = (datetime.now() + timedelta(minutes=15)).strftime("%I:%M %p")
        self.pc_teams_ins.scheduled_meeting(subject="Current meeting", esp_user=self.tc_teams_user, start_time=start_time1, end_time=end_time1)
        time.sleep(5)
        self.tc_teams_room_ins.check_scheduled_meeting_display(subject="Current meeting", organizer_display_name=self.pc_teams_display_name)
        # Schedule an upcoming meeting
        start_time2 = (datetime.now() + timedelta(minutes=30)).strftime("%I:%M %p")
        end_time2 = (datetime.now() + timedelta(minutes=60)).strftime("%I:%M %p")
        self.pc_teams_ins.scheduled_meeting(subject="Upcoming meeting", esp_user=self.tc_teams_user, start_time=start_time2, end_time=end_time2)
        time.sleep(5)
        self.tc_teams_room_ins.check_scheduled_meeting_display(subject="Upcoming meeting", organizer_display_name=self.pc_teams_display_name)
