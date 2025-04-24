import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver
from apollo_base.cmd_driver import CmdDriver
from apollo_jabra.vb_jabra_meeting_driver.driver import VBJabraMeeting
from apollo_swb.driver import init_swb_driver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *

@pytest.mark.usefixtures("cleanup_teams_meeting_in_class")
@pytest.mark.feat_teams_new_meeting_incoming
class TestFeatTeamsNewMeetingIncoming(Base):
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pc_ag_teams_ins = init_apollo_teams_driver()
        self.audio_ins = AudioDriver()
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().get_sys_info["PC_AG_WIN"]["Teams"]["user"]
        self.pc_ag_teams_display_name = Base().get_sys_info["PC_AG_WIN"]["Teams"]["display_name"]
        self.swb_usb = init_swb_driver(Base().swb_ctrl_unit)
        self.swb_hdmi = init_swb_driver("arduino")
        self.vb_jabra_meeting_driver = VBJabraMeeting()

    def teardown(self):
        self.swb_hdmi.disconn_hdmi_from_monitor_hub()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43937, Fif_TC_ESW_109912)
    def test_tc_turn_video_on_off(self):
        # 1 Touch Console user turn the video off
        if self.tc_teams_room_ins.get_camera_status() == "on":
            self.tc_teams_room_ins.turn_camera_off_in_meeting()

        # 2 Verify video invalid, audio valid
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.vb_teams_room_ins.check_dut_camera_video_invalid()

        # 3 Turn off the camera
        self.tc_teams_room_ins.turn_camera_on_in_meeting()

        # 4 Verify video valid, audio valid
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.vb_teams_room_ins.check_dut_camera_video_valid()
        self.pc_ag_teams_ins.check_dut_camera_video_valid(self.tc_teams_user, is_call=False)

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43938, Fif_TC_ESW_109913)
    def test_tc_turn_volume_increase_decrease(self):
        if self.dut_name == "platform_firefoot":
            pytest.skip("Bug 33018: [Firefoot VB] Failed to get the actual volume level via newport command")

        cmd_get_aud_setting = "newport_cmd --function=get-audio-ctrl-current-setup"

        # 1 Touch Console user decrease the volume
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_spk_vol", "lowest")
        get_audio_info = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_aud_setting)
        assert "Speaker Volume current db level: -30" in get_audio_info

        # 2 Touch Console user increase the volume
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_spk_vol", "highest")
        get_audio_info = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_aud_setting)
        assert "Speaker Volume current db level: 0" in get_audio_info

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43946, Fif_TC_ESW_109921)
    def test_tc_incoming_video_on_off(self):
        # 1 Turn the camera on PC AG teams
        self.pc_ag_teams_ins.turn_camera_on_in_meeting()

        # 2 Set the incoming video off from TC
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_incoming_video", "OFF")
        time.sleep(2)

        # 3 Check the the PC teams video is disable from VB
        self.vb_teams_room_ins.check_participant_camera_video_invalid(self.pc_ag_teams_display_name)

        # 4 Set the incoming video off from TC
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_incoming_video", "ON")
        time.sleep(2)

        # 5 Check the the PC teams video is enable from VB
        self.vb_teams_room_ins.check_participant_camera_video_valid(self.pc_ag_teams_display_name)

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43939, Fif_TC_ESW_109914)
    def test_tc_mute_unmute(self):
        # 1 Mute meeting from TC and
        if self.tc_teams_room_ins.get_audio_status() == "on":
            self.tc_teams_room_ins.mute_meeting()

        # 2 check audio with rx and no tx
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # 3 Umute meeting from TC
        self.tc_teams_room_ins.unmute_meeting()

        # 4 check audio with rx and tx again
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43947, Fif_TC_ESW_109922)
    def test_tc_displayed_notification_after_recording_by_tdc(self):
        # 1 TDC starts recording the meeting session
        self.pc_ag_teams_ins.start_recording_in_meeting()
        self.tc_teams_room_ins.check_recording_status(self.pc_ag_teams_user, "ON")

        # 2 Verify a notification will be displayed prominently on the DUT and Touch Console screen
        self.pc_ag_teams_ins.stop_recording_in_meeting()
        self.tc_teams_room_ins.check_recording_status(self.pc_ag_teams_user, "OFF")

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43956, Fif_TC_ESW_109931)
    def test_tc_raise_hand(self):
        # 1 TC raise hand
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_raise_hand", "ON")
        time.sleep(3)
        # 2 PC teams check raise hand on
        self.pc_ag_teams_ins.check_raise_hand_status_in_meeting(self.tc_teams_user, "ON")

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43957, Fif_TC_ESW_109932)
    def test_tc_disabled_hand_raise(self):
        # 1 TC disable raise hand
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_raise_hand", "OFF")
        time.sleep(3)
        # 2 PC teams check raise hand off
        self.pc_ag_teams_ins.check_raise_hand_status_in_meeting(self.tc_teams_user, "OFF")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43958, Fif_TC_ESW_109933)
    def test_tc_verify_live_captions(self):
        logcat_caption_on_cmd = "cat /data/log/logcat.log | grep captionsOn | grep execute | grep successful| wc -l"
        logcat_caption_off_cmd = "cat /data/log/logcat.log | grep captionsOff | grep execute |grep successful| wc -l"

        # 1 Touch Console user click on the Live captions option from more options (...)
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_live_captions", "ON")
        time.sleep(3)
        live_on_count_1 = self.vb_cmd_driver.exec_adb_shell_cmd(logcat_caption_on_cmd, timeout=30)

        # 2 Touch Console user disable the Live caption.
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_live_captions", "OFF")
        time.sleep(3)
        live_off_count_1 = self.vb_cmd_driver.exec_adb_shell_cmd(logcat_caption_off_cmd, timeout=30)

        # 3 turn on again
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_live_captions", "ON")
        time.sleep(3)
        live_on_count_2 = self.vb_cmd_driver.exec_adb_shell_cmd(logcat_caption_on_cmd, timeout=30)

        # 4 turn off again
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_live_captions", "OFF")
        time.sleep(3)
        live_off_count_2 = self.vb_cmd_driver.exec_adb_shell_cmd(logcat_caption_off_cmd, timeout=30)

        # 5 compare the count between 2 times
        assert int(live_on_count_2) == int(live_on_count_1) + 1
        assert int(live_off_count_2) == int(live_off_count_1) + 1

    @pytest.mark.skip(reason="[2024-08-30] Know FW issue block the apollo test: https://dev.azure.com/ONEGN/GN/_workitems/edit/15789")
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43966, Gan_TC_ESW_43965, Fif_TC_ESW_109941, Fif_TC_ESW_109940)
    def test_plug_unplug_hdmi_in_meeting(self):
        # 1 Plug the Hdmi In, Content sharing should start automatically
        self.swb_hdmi.conn_hdmi_to_monitor_hub()
        time.sleep(10)

        # 2 Check the VB and TDC display sharing
        self.vb_teams_room_ins.check_display_as_sharing()
        self.pc_ag_teams_ins.check_participant_sharing_status_in_meeting("ON", self.tc_teams_user)

        # 3 Unplug the HDMI in, Verify that screen share has stopped when the DUT user unplugged the HDMI cable
        self.swb_hdmi.disconn_hdmi_from_monitor_hub()
        time.sleep(5)

        # 4 Check the VB display sharing
        self.vb_teams_room_ins.check_display_as_hdmi_in_disconnect()
        self.pc_ag_teams_ins.check_participant_sharing_status_in_meeting("OFF", self.tc_teams_user)

        # 5 Plug the Hdmi In, Plug the Hdmi In, Content sharing should start automatically
        self.swb_hdmi.conn_hdmi_to_monitor_hub()
        time.sleep(10)

        # 6 Check the VB and TDC display sharing
        self.vb_teams_room_ins.check_display_as_sharing()
        self.pc_ag_teams_ins.check_participant_sharing_status_in_meeting("ON", self.tc_teams_user)

    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43932)
    def test_tc_share_whiteboard(self):
        # 1 DUT click on Share Whiteboard option from more (…) option available on the call control screen
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_whiteboard", "ON")
        self.vb_teams_room_ins.check_whiteboard_status_in_meeting("ON")
        self.pc_ag_teams_ins.check_whiteboard_status_in_meeting("ON")

        # 2 DUT clicks on Stop presenting
        self.tc_teams_room_ins.modify_sp_setting_in_meeting("set_whiteboard", "OFF")
        # work-around: The whiteboard on PC will continue to be shared, need manually stop
        self.pc_ag_teams_ins.stop_whiteboard_sharing_in_meeeting()
        self.vb_teams_room_ins.check_whiteboard_status_in_meeting("OFF")
        self.pc_ag_teams_ins.check_whiteboard_status_in_meeting("OFF")

        # 3 Share whiteboard from PC
        self.pc_ag_teams_ins.share_whiteboard_in_meeting()
        self.vb_teams_room_ins.check_whiteboard_status_in_meeting("ON")
        self.pc_ag_teams_ins.check_whiteboard_status_in_meeting("ON")

        # 4 Stop sharing whiteboard from PC
        self.pc_ag_teams_ins.stop_whiteboard_sharing_in_meeeting()
        self.vb_teams_room_ins.check_whiteboard_status_in_meeting("OFF")
        self.pc_ag_teams_ins.check_whiteboard_status_in_meeting("OFF")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @pytest.mark.usefixtures("create_or_start_teams_meeting_as_guest")
    @jama_tc(Gan_TC_ESW_43949, Gan_TC_ESW_43940, Fif_TC_ESW_109924, Fif_TC_ESW_109915)
    def test_tc_end_meeting(self):
        # 1 TC end the meeting
        self.tc_teams_room_ins.end_meeting()

        # 2 TDC end the meeting
        self.pc_ag_teams_ins.end_meeting()

    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func")
    @pytest.mark.usefixtures("back_to_home")
    @jama_tc(Gan_TC_ESW_43950, Fif_TC_ESW_109925)
    def test_tc_join_meeting_by_conference_bridge_number(self):
        self.pc_ag_teams_ins.initial_meeting()
        meeting_id, meeting_password = self.pc_ag_teams_ins.get_meeting_id_and_passcode()
        self.tc_teams_room_ins.join_meeting(meeting_id=meeting_id, pass_code=meeting_password)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.pc_ag_teams_ins.check_meeting_status("active_unmute")
