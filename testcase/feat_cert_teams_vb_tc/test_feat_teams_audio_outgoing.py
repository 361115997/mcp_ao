import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_audio.driver import AudioDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.usefixtures("cleanup_teams_call")
@pytest.mark.feat_teams_audio_outgoing
class TestTeamsOutgoingCallControl:

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.pc_teams_ins = init_apollo_teams_driver()
        self.audio_ins = AudioDriver()
        self.dut_name = Base().dut_name
        self.pc_ag_teams_user = Base().pc_ag_win["Teams"]["user"]
        self.pc_ag_phone_number = Base().pc_ag_win["Teams"]["phone_number"]

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43903, Gan_TC_ESW_43910, Gan_TC_ESW_43905, Fif_TC_ESW_109880, Fif_TC_ESW_109885, Fif_TC_ESW_109881)
    def test_initial_call_from_home_screen(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.initial_call(self.pc_ag_phone_number, page="home_screen")
        self.pc_teams_ins.check_call_status("incoming_call", self.pc_ag_teams_user)
        self.pc_teams_ins.accept_call()
        time.sleep(10)
        self.tc_teams_room_ins.check_call_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.tc_teams_room_ins.end_call()
        self.tc_teams_room_ins.check_call_status("idle")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43907, Gan_TC_ESW_43908, Fif_TC_ESW_109882, Fif_TC_ESW_109883)
    def test_initial_call_from_more_menu(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.initial_call(self.pc_ag_phone_number, page="more_menu")
        self.pc_teams_ins.check_call_status("incoming_call", self.pc_ag_teams_user)
        self.pc_teams_ins.accept_call()
        time.sleep(10)
        self.tc_teams_room_ins.check_call_status("active_unmute")
        self.audio_ins.verify_call_rx(self.dut_name, "PC_AG_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_AG_WIN")
        self.tc_teams_room_ins.end_call()
        self.tc_teams_room_ins.check_call_status("idle")

    @jama_tc(Gan_TC_ESW_43909, Fif_TC_ESW_109884)
    def test_call_incorrect_number(self):
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.initial_call("+112345", page="home_screen")
        time.sleep(30)
        self.tc_teams_room_ins.check_call_status("idle")

        self.tc_teams_room_ins.initial_call("++11234567890", page="home_screen")
        time.sleep(30)
        self.tc_teams_room_ins.check_call_status("idle")
