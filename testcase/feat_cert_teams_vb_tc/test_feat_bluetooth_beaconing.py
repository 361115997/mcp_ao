import time, pytest
from apollo_teams.driver import init_apollo_teams_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_audio.driver import AudioDriver
from testcase.base import *
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_bluetooth_beaconing
@pytest.mark.usefixtures("enable_bluetooth")
class TestFeatBluetoothBeaconing(Base):

    def setup_class(self):
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.audio_ins = AudioDriver()

    @pytest.mark.usefixtures("re_enable_proximity_join")
    @pytest.mark.usefixtures("cleanup_teams_meeting")
    @pytest.mark.usefixtures("close_meet_now_page")
    @jama_tc(Gan_TC_ESW_43982, Gan_TC_ESW_43986, Fif_TC_ESW_109963, Fif_TC_ESW_109967)
    def test_add_device_as_meeting_room(self):
        # Launch Teams Room to avoid it on other page
        self.pc_ag_teams_ins.cancel_scheduled_meeting()
        self.tc_teams_room_ins.open()
        self.pc_ag_teams_ins.handle_meet_now().open()
        self.pc_ag_teams_ins.handle_meet_now().check_room_available(esp_user=self.tc_teams_user)
        # The right behavior is that when added from the nearby device, the call should be automatically answered.
        # But it always can't display in the nearby device list, so we can't test it.
        # Aligned with Jodi, automatic part test with manual answer and [+M] on Jama testcase. Manual test team will verify the auto answer part.
        self.pc_ag_teams_ins.handle_meet_now().meet_now_with(esp_user=self.tc_teams_user)
        time.sleep(10)
        # By fw design: TC may take the phone call automatically while using bluetooth beaconing feature
        if self.dut_name == "platform_gandalf":
            if not self.tc_teams_room_ins.is_sp_in_meeting():
                self.tc_teams_room_ins.check_meeting_status("incoming_call")
                self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.pc_ag_teams_ins.check_meeting_status("audio_off")
        self.pc_ag_teams_ins.check_camera_status_in_meeting("off")
        # Try exit the meeting room
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 200 960 1600 960 1000")
        time.sleep(1)
        self.tc_cmd_driver.exec_adb_shell_cmd("input swipe 1600 960 200 960 1000")
        time.sleep(5)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")

    @pytest.mark.usefixtures("start_meeting_via_bluetooth_beaconing")
    @pytest.mark.usefixtures("close_meet_now_page")
    @pytest.mark.usefixtures("re_enable_proximity_join")
    @pytest.mark.usefixtures("cleanup_teams_meeting")
    @jama_tc(Gan_TC_ESW_43987, Gan_TC_ESW_43985, Fif_TC_ESW_109968, Fif_TC_ESW_109966)
    def test_room_status_in_call(self):
        # make sure ep don't have ongoing meeting to avoid block running next step: handle_meet_now().open()
        self.pc_ep_teams_ins.cleanup_sp_meeting()

        self.pc_ep_teams_ins.handle_meet_now().open()
        self.pc_ep_teams_ins.handle_meet_now().check_room_in_call(self.tc_teams_user)
        self.pc_ep_teams_ins.handle_meet_now().close()

    @pytest.mark.usefixtures("start_meeting_via_bluetooth_beaconing")
    @pytest.mark.usefixtures("close_meet_now_page")
    @pytest.mark.usefixtures("re_enable_proximity_join")
    @pytest.mark.usefixtures("cleanup_teams_meeting")
    @jama_tc(Gan_TC_ESW_43984, Fif_TC_ESW_109965)
    def test_ignore_incoming_call(self):
        # make sure ep don't have ongoing meeting to avoid block running next step: handle_meet_now().open()
        self.pc_ep_teams_ins.cleanup_sp_meeting()

        self.pc_ep_teams_ins.initial_call(self.tc_teams_user)
        time.sleep(3)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        try:
            self.tc_teams_room_ins.check_meeting_status("incoming_call")
            rst = True
        except:
            rst = False
        assert not rst, "The incoming call is not be ignored when the room is in a meeting."
        self.pc_ep_teams_ins.end_call(self.tc_teams_user)

    @pytest.mark.usefixtures("start_meeting_via_bluetooth_beaconing")
    @pytest.mark.usefixtures("close_meet_now_page")
    @pytest.mark.usefixtures("re_enable_proximity_join")
    @pytest.mark.usefixtures("cleanup_teams_meeting")
    @jama_tc(Gan_TC_ESW_43983, Fif_TC_ESW_109964)
    def test_disconnect_meeting(self):
        self.tc_teams_room_ins.end_meeting()
        self.tc_teams_room_ins.check_meeting_status("idle")
        self.pc_ag_teams_ins.leave_meeting()
