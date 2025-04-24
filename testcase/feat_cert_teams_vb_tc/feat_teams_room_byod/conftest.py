import os, json, pytest, time
from apollo_base.systemlogger import Logger
from testcase.base import *
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_swb.driver import init_swb_driver


@pytest.fixture(scope="function")
def create_or_start_teams_byod_meeting():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    teams_ag_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    teams_ep_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")
    tc_jabra_meeting_driver = TCJabraMeeting()
    teams_ag_user = Base().pc_ag_win["Teams"]["user"]  # "gnlabauto03@jabralab.onmicrosoft.com"
    teams_ep_user = Base().pc_ep_win["Teams"]["user"]  # "gnlabauto02@jabralab.onmicrosoft.com"
    teams_ag_ins.open()
    teams_ep_ins.open()
    try:
        teams_ag_ins.check_meeting_status("active_unmute")
        teams_ep_ins.check_meeting_status("active_unmute")
        tc_jabra_meeting_driver.byod_page().is_on_teams_byod_mode()
        teams_ag_ins.turn_camera_on_in_meeting()
        Logger.ins().std_logger().info("Already exists teams byod meeting, no need create!!!")
    except:
        Logger.ins().std_logger().info("No exists teams byod meeting, create one...")
        # Clean byod meeting
        teams_ep_ins.cleanup_sp_meeting()
        teams_ag_ins.cleanup_sp_meeting()
        # Switch to BYOD mode
        if not tc_jabra_meeting_driver.byod_page().is_on_teams_byod_mode():
            tc_teams_room_ins.open()
            time.sleep(10)
            tc_teams_room_ins.check_sp_status("home_ready")
            tc_teams_room_ins.goto_jabra_meeting()
            tc_jabra_meeting_driver.home_page().goto_admin()
            tc_jabra_meeting_driver.admin_page().goto_system_page()
            tc_jabra_meeting_driver.system_page().enable_teams_byod()
            # tc_jabra_meeting_driver.home_page().close_home_page()
            Logger.ins().std_logger().info("Enabled byod done")

        # Establish a new meeting
        teams_ep_ins.initial_meeting()
        time.sleep(2)
        teams_ep_ins.invite_people_into_meeting(teams_ag_user)
        time.sleep(10)
        teams_ag_ins.check_meeting_status("incoming_call")
        teams_ag_ins.accept_meeting_invite_request()
        time.sleep(10)
        # Check the Call status
        teams_ag_ins.check_meeting_status("active_unmute")
        teams_ag_ins.turn_camera_on_in_meeting()


def goto_teams_byod():
    tc_jabra_meeting_driver = TCJabraMeeting()
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    # tc_teams_room_ins.goto_home()
    if not tc_jabra_meeting_driver.byod_page().is_on_teams_byod_mode():
        tc_teams_room_ins.open()
        time.sleep(10)
        tc_teams_room_ins.check_sp_status("home_ready")
        tc_teams_room_ins.goto_jabra_meeting()
        tc_jabra_meeting_driver.home_page().goto_admin()
        tc_jabra_meeting_driver.admin_page().goto_system_page()
        tc_jabra_meeting_driver.system_page().enable_teams_byod()
        Logger.ins().std_logger().info("Enabled byod done")

@pytest.fixture(scope="function")
def enable_teams_byod():
    goto_teams_byod()


@pytest.fixture(scope="function")
def yield_swb_usb_connect():
    yield
    swb_usb = init_swb_driver(Base().swb_ctrl_unit)
    swb_usb.conn_dut_to_apollo(Base().dut_name)
    time.sleep(3)
    # Call the goto_teams_byod()
    goto_teams_byod()
