import pytest, time

from apollo_audio.driver import AudioDriver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_teams_room.driver import init_teams_room_driver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.feat_teams_console_escalate_to_conference
@pytest.mark.usefixtures("cleanup_teams_call", "cleanup_teams_meeting")
class TestFeatTeamsConsoleEscalateToConference(Base):

    def setup_class(self):
        self.audio_ins = AudioDriver()
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")
        self.tc_teams_user = Base().tc_teams["user"]
        self.pc_ag_teams_user = Base().get_sys_info["PC_AG_WIN"]["Teams"]["user"]
        self.pc_ep_teams_user = Base().get_sys_info["PC_EP_WIN"]["Teams"]["user"]
        self.pc_ag_teams_phone_number = Base().get_sys_info["PC_AG_WIN"]["Teams"]["phone_number"]
        self.pc_ep_teams_phone_number = Base().get_sys_info["PC_EP_WIN"]["Teams"]["phone_number"]

    @jama_tc(Gan_TC_ESW_43919, Fif_TC_ESW_109895)
    def test_add_pstn_while_in_call_with_tdc(self):
        # Initial call with TDC
        self.pc_ep_teams_ins.initial_call(self.tc_teams_user)
        time.sleep(5)
        self.tc_teams_room_ins.check_meeting_status("incoming_call")
        self.tc_teams_room_ins.accept_meeting_invite_request()
        time.sleep(10)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.pc_ep_teams_ins.check_call_status("active_unmute", self.tc_teams_user)
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")
        # Add call with PSTN
        self.tc_teams_room_ins.invite_people_into_meeting(self.pc_ag_teams_phone_number)
        self.pc_ag_teams_ins.check_call_status("incoming_call", self.tc_teams_user)
        self.pc_ag_teams_ins.accept_call()
        time.sleep(5)
        self.pc_ag_teams_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43922, Fif_TC_ESW_109898)
    def test_add_tdc_while_in_call_with_tdc(self):
        # Initial call with TDC
        self.pc_ep_teams_ins.initial_call(self.tc_teams_user)
        time.sleep(5)
        self.tc_teams_room_ins.check_meeting_status("incoming_call")
        self.tc_teams_room_ins.accept_meeting_invite_request()
        time.sleep(10)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.pc_ep_teams_ins.check_call_status("active_unmute", self.tc_teams_user)
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")
        # Add call with TDC
        self.tc_teams_room_ins.invite_people_into_meeting(self.pc_ag_teams_user)
        self.pc_ag_teams_ins.check_call_status("incoming_call", self.tc_teams_user)
        self.pc_ag_teams_ins.accept_call()
        time.sleep(5)
        self.pc_ag_teams_ins.check_call_status("active_unmute", self.tc_teams_user)
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")

    @jama_tc(Gan_TC_ESW_43925, Fif_TC_ESW_109901)
    @pytest.mark.skip(
        reason="The PSTN call will change to Teams network call automatically and not enough PSTN accounts")
    def test_add_pstn_while_in_call_with_pstn(self):
        # Initial call with PSTN
        self.tc_teams_room_ins.initial_call(self.pc_ep_teams_phone_number)
        time.sleep(5)
        self.pc_ep_teams_ins.check_call_status("incoming_call", self.pc_ep_teams_phone_number)
        self.pc_ep_teams_ins.accept_call()
        time.sleep(10)
        self.pc_ep_teams_ins.check_call_status("active_unmute", self.tc_teams_user)
        self.tc_teams_room_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")
        # Add call with PSTN
        # Workaround: the pstn call will change to teams netowrk call automatic, we have pstn accounts limiit, here we use netwrok call instead 
        self.tc_teams_room_ins.invite_people_into_meeting(self.pc_ag_teams_phone_number)
        self.pc_ag_teams_ins.check_meeting_status("incoming_call")
        self.pc_ag_teams_ins.accept_meeting_invite_request()
        time.sleep(5)
        self.pc_ag_teams_ins.check_meeting_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
