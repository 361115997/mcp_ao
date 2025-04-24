import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.systemlogger import Logger
from apollo_teams.driver import init_apollo_teams_driver
from testcase.base import *




@pytest.fixture(scope="function")
def create_or_start_teams_meeting_as_guest():
    tc_teams_user = Base().tc_teams["user"]
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    pc_ag_teams_ins.open()
    if not (tc_teams_room_ins.is_sp_in_meeting(role="guest") and pc_ag_teams_ins.is_sp_in_meeting(role="host")):
        # Cleanup existing meeting
        tc_teams_room_ins.cleanup_sp_meeting()
        pc_ag_teams_ins.cleanup_sp_meeting()
        time.sleep(2)
        # Create new meeting from PC
        pc_ag_teams_ins.initial_meeting()
        time.sleep(2)
        pc_ag_teams_ins.invite_people_into_meeting(tc_teams_user)
        time.sleep(10)
        tc_teams_room_ins.check_meeting_status("incoming_call")
        tc_teams_room_ins.accept_meeting_invite_request()
        time.sleep(10)
        # Check the Meeting status
        tc_teams_room_ins.check_meeting_status("active_unmute")


@pytest.fixture(scope="function")
def create_or_start_teams_meeting_as_host():
    teams_ag_user = Base().pc_ag_win["Teams"]["user"]
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    pc_ag_teams_ins.open()
    if not (tc_teams_room_ins.is_sp_in_meeting(role="host") and pc_ag_teams_ins.is_sp_in_meeting(role="guest")):
        # Cleanup existing meeting
        tc_teams_room_ins.cleanup_sp_meeting()
        pc_ag_teams_ins.cleanup_sp_meeting()
        time.sleep(2)
        # Create new meeting from PC
        tc_teams_room_ins.initial_meeting()
        time.sleep(2)
        tc_teams_room_ins.invite_people_into_meeting(teams_ag_user)
        time.sleep(10)
        pc_ag_teams_ins.check_meeting_status("incoming_call")
        pc_ag_teams_ins.accept_meeting_invite_request()
        time.sleep(10)
        # Check the Meeting status
        pc_ag_teams_ins.check_meeting_status("active_unmute")


@pytest.fixture(scope="function")
def stop_sharing_in_func():
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    yield
    pc_ag_teams_ins.stop_share_in_meeting()


