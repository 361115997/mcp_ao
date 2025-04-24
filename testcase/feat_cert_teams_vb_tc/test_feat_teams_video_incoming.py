import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.feat_teams_video_incoming
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.usefixtures("create_or_start_teams_call_via_ep")
class TestFeatIncomingVideoCallControl:

    def setup_class(self):
        self.dut_name = Base().dut_name
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.audio_ins = AudioDriver()
        self.pc_teams_ins = init_apollo_teams_driver()
        self.tc_teams_user = Base().tc_teams["user"]

    @jama_tc(Gan_TC_ESW_43915, Gan_TC_ESW_43914, Fif_TC_ESW_109889, Fif_TC_ESW_109888)
    def test_dut_puts_call_on_mute(self):
        # Check camera is on and audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.pc_teams_ins.check_dut_camera_video_valid(self.tc_teams_user)

        # Mute Call from TC and check audio with rx and no tx
        self.tc_teams_room_ins.mute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # Umute Call from TC and check audio with rx and tx again
        self.tc_teams_room_ins.unmute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43913, Gan_TC_ESW_43912, Fif_TC_ESW_109887, Fif_TC_ESW_109886)
    def test_dut_puts_call_on_hold(self):
        # Check camera is on and audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.pc_teams_ins.check_dut_camera_video_valid(self.tc_teams_user)

        # Hold Call from TC and check audio with no rx and no tx
        self.tc_teams_room_ins.hold_meeting()
        self.tc_teams_room_ins.check_meeting_status("onhold")
        self.audio_ins.verify_call_no_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # Resume Call from TC and check audio with rx and tx again
        self.tc_teams_room_ins.resume_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")

        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.pc_teams_ins.check_dut_camera_video_valid(self.tc_teams_user)

    @jama_tc(Gan_TC_ESW_43916, Fif_TC_ESW_109890)
    def test_dut_puts_call_on_mute_with_video_enabled(self):
        # Check camera is on and audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

        # Mute Call from TC and check audio with rx and no tx self.tc_teams_room_ins.mute_meeting()
        self.tc_teams_room_ins.mute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # Umute Call from TC and check audio with rx and tx again
        self.tc_teams_room_ins.unmute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43898, Fif_TC_ESW_109875)
    def test_video_call_to_dut(self):
        # Check camera is on and audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.pc_teams_ins.check_dut_camera_video_valid(self.tc_teams_user)

        # End call from TC and check call status is idle
        self.tc_teams_room_ins.end_meeting()
        time.sleep(10)
        self.tc_teams_room_ins.check_meeting_status("idle")
