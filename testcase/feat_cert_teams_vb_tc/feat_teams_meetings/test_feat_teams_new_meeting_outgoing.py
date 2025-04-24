import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver
from apollo_base.cmd_driver import CmdDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *

@pytest.mark.usefixtures("cleanup_teams_meeting_in_class")
@pytest.mark.feat_teams_new_meeting_outgoing
class TestFeatTeamsNewMeetingOutgoing(Base):
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pc_ag_teams_ins = init_apollo_teams_driver()
        self.pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")
        self.audio_ins = AudioDriver()
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().get_sys_info["PC_AG_WIN"]["Teams"]["user"]
        self.pc_ag_teams_display_name = Base().get_sys_info["PC_AG_WIN"]["Teams"]["display_name"]

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43948, Fif_TC_ESW_109923)
    def test_tc_menu_bar_can_be_dismissed_after_clicking_outside(self):
        # 1 Touch Console user clicks on the menu more (...) option
        # Touch Console user touches or click outside of the menu bar area
        self.tc_teams_room_ins.dismiss_menu()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43942, Fif_TC_ESW_109917)
    def test_tc_see_others_participants(self):
        # 1 Observe the Touch Console
        # Verify Touch Console user can see the list of participants on the screen
        self.tc_teams_room_ins.check_participant_exists(self.pc_ag_teams_display_name)

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43941, Fif_TC_ESW_109916)
    def test_tc_mute_others(self):
        # 1 Make sure TDC is ummuted
        if self.pc_ag_teams_ins.get_audio_status_in_meeting() == "OFF":
            self.pc_ag_teams_ins.unmute_meeting()
            time.sleep(2)

        # 2 Mute the TDC
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("mute_others", self.pc_ag_teams_display_name)

        # 3 Check the TDC is muted
        self.pc_ag_teams_ins.check_meeting_status("active_mute")

        # 4 Unmute from the TDC
        self.pc_ag_teams_ins.unmute_meeting()

    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43951, Fif_TC_ESW_109926)
    def test_verify_layout_during_sharing_content(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 TC Verify the shared content on the DUT
        self.tc_teams_room_ins.check_layout_options()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43952, Fif_TC_ESW_109927)
    def test_verify_layout_gallery_content_people(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 TC set the layout as gallery_content_people
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_gallery", "content_people")
        self.vb_teams_room_ins.check_share_content_status_in_meeting("gallery_content_people", "ON")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43933, Gan_TC_ESW_43953, Fif_TC_ESW_109908, Fif_TC_ESW_109928)
    def test_verify_layout_gallery_people_only(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 TC set the layout as gallery_people_only
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_gallery", "people_only")
        self.vb_teams_room_ins.check_share_content_status_in_meeting("gallery_people_only", "ON")

    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    def test_verify_layout_front_row(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 TC set the layout as gallery_flont_row
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_gallery", "flont_row")
        self.vb_teams_room_ins.check_share_content_status_in_meeting("gallery_flont_row", "ON")

    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    def test_verify_layout_gallery_focus_on_content(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 TC set the layout as focus_on_content
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_gallery", "focus_on_content")
        self.vb_teams_room_ins.check_share_content_status_in_meeting("focus_on_content", "ON")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("stop_sharing_in_func")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    @jama_tc(Gan_TC_ESW_43945, Fif_TC_ESW_109920)
    def test_vb_view_shared_content(self):
        # 1 TDC1 shares content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.share_content_in_meeting()
        time.sleep(3)

        # 2 Verify the shared content on the DUT
        self.vb_teams_room_ins.check_share_content_status_in_meeting("gallery", "ON")
        time.sleep(5)

        # 3 TDC1 stop share content (Desktop or file ) in the meeting
        self.pc_ag_teams_ins.stop_share_in_meeting()
        time.sleep(3)
        self.vb_teams_room_ins.check_share_content_status_in_meeting("gallery", "OFF")

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_host")
    def test_tc_remove_participants_from_meeting(self):
        # 1 Check the Meeting status
        self.pc_ag_teams_ins.check_meeting_status("active_unmute")

        # 2 Remove PC Teams AG
        self.tc_teams_room_ins.remove_people_from_meeting(self.pc_ag_teams_display_name)
        self.pc_ag_teams_ins.check_been_removed_from_meeting()
