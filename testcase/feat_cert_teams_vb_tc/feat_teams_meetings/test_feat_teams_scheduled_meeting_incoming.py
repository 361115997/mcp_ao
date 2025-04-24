import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver
from apollo_base.cmd_driver import CmdDriver
from testcase.base import Base
from datetime import datetime, timedelta
from apollo_base.systemlogger import Logger
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *

@pytest.mark.usefixtures("cleanup_teams_meeting_in_class")
@pytest.mark.feat_teams_scheduled_meeting_incoming
class TestFeatTeamsScheduledMeetingIncoming(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pc_ag_teams_ins = init_apollo_teams_driver()
        self.audio_ins = AudioDriver()
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().get_sys_info["PC_AG_WIN"]["Teams"]["user"]
        self.pc_ag_teams_display_name = Base().get_sys_info["PC_AG_WIN"]["Teams"]["display_name"]
        self.pc_ag_teams_phone_number = Base().get_sys_info["PC_AG_WIN"]["Teams"]["phone_number"]
        self.meeting_title = f'Meeting with {datetime.now().strftime("%Y%m%d")}'
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.tc_teams_room_ins.cleanup_sp_meeting()
        self.pc_ag_teams_ins.cleanup_sp_meeting()

    def teardown_class(self):
        self.pc_ag_teams_ins.cancel_scheduled_meeting()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43926, Fif_TC_ESW_109902)
    def test_scheduled_meeting_should_sync_automatically_on_dut(self):
        self.vb_cmd_driver.exec_adb_shell_cmd("jose_service_controller system --set-24hour-time-format True")
        time_format = "%H:%M"
        meeting_title = self.meeting_title.replace("Meeting with ", "")
        # 1 Scheduled meeting from TDC
        self.pc_ag_teams_ins.scheduled_meeting(self.meeting_title, self.tc_teams_user)
        time.sleep(10)
        # 2 Verify meeting created by TDC1 should automatically sync on DUT and Touch Console device.
        # Verify meeting displays the name of organizer
        self.tc_teams_room_ins.check_scheduled_meeting_display(meeting_title, self.pc_ag_teams_display_name)

        # 3 Verify the date
        meeting_date = self.tc_teams_room_ins.get_scheduled_meeting_date(self.meeting_title)
        dt1 = datetime.strptime(meeting_date.split()[2], time_format)
        dt2 = datetime.strptime(meeting_date.split()[-1], time_format)
        time_difference = dt1 - dt2  # Book all day meeting, the time difference only 60s
        assert time_difference.seconds == 3600 * 1 / 60

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43928, Gan_TC_ESW_43927, Fif_TC_ESW_109904, Fif_TC_ESW_109903)
    def test_scheduled_meeting_time_synced_with_time_zone_on_dut(self):
        # 0 Initial the time format to 24
        self.vb_cmd_driver.exec_adb_shell_cmd("jose_service_controller system --set-24hour-time-format True")
        time_format = "%H:%M"
        # 1 Scheduled meeting from TDC
        self.pc_ag_teams_ins.scheduled_meeting(self.meeting_title, self.tc_teams_user)

        # 2 Navigate to device settings and change the time zone on the Touch Console to IST(GMT +5.30 hours).
        self.vb_cmd_driver.exec_adb_shell_cmd("jose_service_controller system --set-timezone Etc/GMT+5")
        time.sleep(10)
        meeting_date = self.tc_teams_room_ins.get_scheduled_meeting_date(self.meeting_title)  # June 17, 11:00 - June 18, 10:59
        dt1 = datetime.strptime(meeting_date.split()[-1], time_format)

        # 3 Navigate to device settings and change the time zone on the Touch Console device to London (GMT + 00).
        self.vb_cmd_driver.exec_adb_shell_cmd("jose_service_controller system --set-timezone Etc/GMT+0")
        time.sleep(10)
        meeting_date = self.tc_teams_room_ins.get_scheduled_meeting_date(self.meeting_title)  # June 17, 16:00 - June 18, 15:59
        dt2 = datetime.strptime(meeting_date.split()[-1], time_format)
        time_difference = dt2 - dt1
        Logger.ins().std_logger().info(f"time_difference dt1 and dt2={time_difference.seconds/3600}h")
        assert time_difference.seconds == 3600 * 5

        # 4 Again, Navigate to device settings and change the time zone to GMT-8.00 on the Touch Console device.
        self.vb_cmd_driver.exec_adb_shell_cmd("jose_service_controller system --set-timezone Etc/GMT-8")
        time.sleep(10)
        meeting_date = self.tc_teams_room_ins.get_scheduled_meeting_date(self.meeting_title)  # 00:00 - 23:59
        dt3 = datetime.strptime(meeting_date.split()[-1], time_format)
        time_difference = dt3 - dt2
        Logger.ins().std_logger().info(f"time_difference dt2 and dt3={time_difference.seconds/3600}h")
        assert time_difference.seconds == 3600 * 8

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func")
    @jama_tc(Gan_TC_ESW_43954, Gan_TC_ESW_43930, Gan_TC_ESW_43929, Fif_TC_ESW_109929, Fif_TC_ESW_109906, Fif_TC_ESW_109905)
    def test_scheduled_meeting_joined(self):
        # 1 Scheduled meeting from TDC
        self.pc_ag_teams_ins.scheduled_meeting(self.meeting_title, self.tc_teams_user)

        # 2 Verify a progress screen (connecting) is displayed on the DUT and Touch Console screen while connecting to the meeting.
        self.tc_teams_room_ins.join_scheduled_meeting()

        # 3 Verify Call Controls bar with all the control options mute, hang-up, volume increase/decrease option should appear on the screen once call is connected.
        self.tc_teams_room_ins.check_control_options_in_meeting()

        # 4 Verify view other participant not join yet
        self.tc_teams_room_ins.check_yet_not_participant_in_meeting(self.pc_ag_teams_display_name)

        # 5 End Meeting
        self.tc_teams_room_ins.end_meeting()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func")
    @jama_tc(Gan_TC_ESW_43943, Fif_TC_ESW_109918)
    def test_tc_invite_pstn_user(self):
        # 1 Scheduled meeting from TDC
        self.pc_ag_teams_ins.scheduled_meeting(self.meeting_title, self.tc_teams_user)
        time.sleep(3)

        # 2 Verify a progress screen (connecting) is displayed on the DUT and Touch Console screen while connecting to the meeting.
        self.tc_teams_room_ins.join_scheduled_meeting()
        time.sleep(60)  # Waiting for the Join prompt dismiss auto

        # 3 Invite the PSTN user
        self.tc_teams_room_ins.invite_people_into_meeting(self.pc_ag_teams_phone_number)

        # 4 Check the Incoming call
        self.pc_ag_teams_ins.check_meeting_status("incoming_call")
        self.pc_ag_teams_ins.accept_meeting_invite_request()
        time.sleep(5)

        # 5 Check the Meeting status
        self.pc_ag_teams_ins.check_meeting_status("active_unmute")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func", "back_to_home_in_func")
    @jama_tc(Gan_TC_ESW_43936, Fif_TC_ESW_109911)
    def test_vb_see_preview_video_stream(self):
        # 1 New meeting from home
        self.tc_teams_room_ins.initial_meeting()

        # 2 Check VB Preview
        self.vb_teams_room_ins.check_preview_video_on()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func", "back_to_home_in_func")
    @jama_tc(Gan_TC_ESW_43959, Fif_TC_ESW_109934)
    def test_tc_new_meeting_from_home(self):
        # 1 New meeting from home
        self.tc_teams_room_ins.initial_meeting()
        time.sleep(3)
        self.tc_teams_room_ins.end_meeting()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func", "back_to_home_in_func")
    @jama_tc(Gan_TC_ESW_43960, Fif_TC_ESW_109935)
    def test_tc_new_meeting_from_more_option(self):
        # 1 New meeting from home
        self.tc_teams_room_ins.initial_meeting_from_more()
        time.sleep(3)
        self.tc_teams_room_ins.end_meeting()

    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func", "back_to_home_in_func")
    @jama_tc(Gan_TC_ESW_43967, Fif_TC_ESW_109942)
    def test_hdmi_options_in_appui(self):
        # 1 Goto AppUI -> Admin-> General -> Service Provider -> Teams Admin setting -> Meetings
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_jabra_meeting()

        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_general_page()
        self.tc_jabra_meeting_driver.general_page().goto_service_provider()

        # 2 Check  option:-1.Wallpaper2.Enable HDMI content sharing   a.Include audio   b.Automatically share to the room display
        self.tc_jabra_meeting_driver.general_page().open_teams_access_settings()
        self.tc_jabra_meeting_driver.general_page().check_teams_access_settings_meetings_ui()

        # 3 Click back button in Teams Admin Settings page
        self.tc_jabra_meeting_driver.general_page().click_back_in_teams_access_settings()
        time.sleep(5)
        self.tc_jabra_meeting_driver.admin_page().check_admin_page()
        self.tc_jabra_meeting_driver.admin_page().close_admin_page()
        self.tc_jabra_meeting_driver.home_page().close_home_page()
