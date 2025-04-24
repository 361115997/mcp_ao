import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_audio.driver import AudioDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.usefixtures("create_or_start_teams_call_via_ep")
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_audio_incoming
class TestTeamsCallEstablished:

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.audio_ins = AudioDriver()
        self.dut_name = Base().dut_name
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)

    @jama_tc(Gan_TC_ESW_43913, Gan_TC_ESW_43912, Fif_TC_ESW_109887, Fif_TC_ESW_109886)
    def test_dut_puts_call_on_hold(self):
        # Check Audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

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

    @jama_tc(Gan_TC_ESW_43915, Gan_TC_ESW_43914, Gan_TC_ESW_44799, Gan_TC_ESW_44800, Fif_TC_ESW_109889, Fif_TC_ESW_109888, Fif_TC_ESW_109893, Fif_TC_ESW_109894)
    def test_dut_puts_call_on_mute(self):
        # Check Audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

        # Mute Call from TC and check audio with rx and no tx
        self.tc_cmd_driver.exec_adb_shell_cmd("logcat -c")
        self.vb_cmd_driver.exec_adb_shell_cmd("logcat -c")
        self.tc_teams_room_ins.mute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        tc_mute_intent = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep com.microsoft.skype.teams.ipphone.APP_MUTE_STATE")
        assert "MUTE_STATE 1" in tc_mute_intent, "The mute intent is not sent to the DUT."
        vb_mute_intent = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep com.microsoft.skype.teams.ipphone.APP_MUTE_STATE")
        assert "MUTE_STATE 1" in vb_mute_intent, "The mute intent is not sent to the DUT."
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # Umute Call from TC and check audio with rx and tx again
        self.tc_teams_room_ins.unmute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        tc_unmute_intent = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep com.microsoft.skype.teams.ipphone.APP_MUTE_STATE")
        assert "MUTE_STATE 0" in tc_unmute_intent, "The unmute intent is not sent to the DUT."
        vb_unmute_intent = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep com.microsoft.skype.teams.ipphone.APP_MUTE_STATE")
        assert "MUTE_STATE 0" in vb_unmute_intent, "The unmute intent is not sent to the DUT."
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43918, Fif_TC_ESW_109892)
    def test_hold_muted_call(self):
        # Mute Call from TC and check audio with rx and no tx
        self.tc_teams_room_ins.mute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # After few seconds Touch Console user hold the call
        self.tc_teams_room_ins.hold_meeting()
        self.tc_teams_room_ins.check_meeting_status("onhold")
        self.audio_ins.verify_call_no_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # After 1 minute Touch Console user resumes the call
        time.sleep(60)
        self.tc_teams_room_ins.resume_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_mute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_AG_WIN")

        # Umute Call from TC and check audio with rx and tx again
        self.tc_teams_room_ins.unmute_meeting()
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43899, Fif_TC_ESW_109876)
    def test_audio_call_to_dut(self):
        # Check Audio is working
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

        # End call from TC and check call status is idle
        self.tc_teams_room_ins.end_meeting()
        time.sleep(10)
        self.tc_teams_room_ins.check_meeting_status("idle")

@pytest.mark.feat_teams_audio_incoming
@pytest.mark.usefixtures("cleanup_teams_call")
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
class TestTeamsIncomingPstnCall(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.pc_teams_ins = init_apollo_teams_driver()
        self.audio_ins = AudioDriver()
        self.tc_teams_phone_number = Base().tc_teams["phone_number"]

    @jama_tc(Gan_TC_ESW_43900, Fif_TC_ESW_109877)
    def test_tc_receive_call_from_pstn_user(self):
        # Initial call from PC to TC
        self.pc_teams_ins.initial_call(self.tc_teams_phone_number)
        self.tc_teams_room_ins.check_meeting_status("incoming_call", timeout=15)
        self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.check_meeting_status("active_unmute", timeout=15)
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.tc_teams_room_ins.end_meeting()
        self.tc_teams_room_ins.check_meeting_status("idle", timeout=10)



@pytest.mark.feat_teams_audio_incoming
@pytest.mark.usefixtures("cleanup_teams_call")
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
class TestTeamsCallNoEstablished:

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.pc_teams_ins = init_apollo_teams_driver()
        self.audio_ins = AudioDriver()
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().pc_ag_win["Teams"]["user"]
        self.pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")

    def test_tc_declines_call(self):
        # Initial call from PC to TC
        self.pc_teams_ins.initial_video_call(self.tc_teams_user)
        self.tc_teams_room_ins.check_meeting_status("incoming_call")
        # Reject call from TC
        self.tc_teams_room_ins.reject_meeting_invite_request()
        time.sleep(5)
        self.tc_teams_room_ins.check_meeting_status("idle")

    def test_tc_not_answer_call(self):
        # Initial call from PC to TC
        self.pc_teams_ins.initial_video_call(self.tc_teams_user)
        self.tc_teams_room_ins.check_meeting_status("incoming_call")

        # Wait for 60s to expire incoming call
        time.sleep(60)
        self.tc_teams_room_ins.check_meeting_status("idle")

    @jama_tc(Gan_TC_ESW_43917, Fif_TC_ESW_109891)
    def test_dut_should_not_get_second_incoming_call(self):
        # Initial call from PC to TC
        self.pc_teams_ins.initial_video_call(self.tc_teams_user)
        self.tc_teams_room_ins.check_meeting_status("incoming_call", timeout=15)
        self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.check_meeting_status("active_unmute", timeout=15)
        self.pc_ep_teams_ins.initial_call(self.tc_teams_user)
        self.tc_teams_room_ins.check_meeting_status("active_unmute", timeout=5)
        try:
            self.tc_teams_room_ins.check_call_status("incoming_call")
            rst = False
        except:
            rst = True

        assert rst, "The incoming call is not be ignored when the room is in a meeting."
