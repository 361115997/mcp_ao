import pytest, time
from datetime import datetime, timedelta
from apollo_teams.driver import init_apollo_teams_driver
from apollo_teams_room.driver import init_teams_room_driver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.feat_teams_console_hard_mute
@pytest.mark.usefixtures("cleanup_teams_meeting")
class TestFeatTeamsConsoleHardMute(Base):

    def setup_class(self):
        self.pc_ag_teams_ins = init_apollo_teams_driver()
        self.tc_teams_room = init_teams_room_driver(test_device="TC")
        self.tc_teams_user = Base().tc_teams["user"]
        self.tc_teams_room.open()

    def teardown_class(self):
        self.tc_teams_room.open()
        self.pc_ag_teams_ins.cancel_scheduled_meeting()

    @jama_tc(Gan_TC_ESW_43981, Fif_TC_ESW_109957)
    def test_disable_mic_and_camera_for_attendees_options(self):
        # Schedule an upcoming meeting
        start_time = (datetime.now() - timedelta(minutes=15)).strftime("%I:%M %p")
        end_time = (datetime.now() + timedelta(minutes=15)).strftime("%I:%M %p")
        self.pc_ag_teams_ins.scheduled_meeting("Test", self.tc_teams_user, start_time, end_time)
        self.tc_teams_room.join_scheduled_meeting()

        self.tc_teams_room.check_participant_settings()
        self.tc_teams_room.end_meeting()
