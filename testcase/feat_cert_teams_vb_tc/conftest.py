import pytest, time
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.systemlogger import Logger
from apollo_teams.driver import init_apollo_teams_driver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_base.cmd_driver import CmdDriver
from testcase.base import *
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting


@pytest.fixture(scope="function")
def cleanup_teams_meeting_in_func():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()
    yield
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()

@pytest.fixture(scope="class")
def cleanup_teams_meeting_in_class():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()
    yield
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()

@pytest.fixture(scope="function")
def back_to_home_in_func():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_teams_room_ins.open()
    yield
    tc_teams_room_ins.open()


@pytest.fixture(scope="function")
def cleanup_teams_call():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")

    tc_teams_room_ins.cleanup_sp_meeting()
    pc_ag_teams_ins.cleanup_sp_call()
    pc_ep_teams_ins.cleanup_sp_call()
    yield
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_ag_teams_ins.cleanup_sp_call()
    pc_ep_teams_ins.cleanup_sp_call()


@pytest.fixture(scope="function")
def cleanup_teams_meeting():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()
    yield
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_teams_ins.cleanup_sp_meeting()


@pytest.fixture(scope="class")
def establish_video_call():
    tc_teams_user = Base().tc_teams["user"]
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")

    pc_teams_ins.initial_video_call(tc_teams_user)
    time.sleep(5)
    tc_teams_room_ins.check_meeting_status("incoming_call")
    tc_teams_room_ins.accept_meeting_invite_request()
    time.sleep(10)
    tc_teams_room_ins.check_meeting_status("active_unmute")

    yield
    tc_teams_room_ins.end_meeting()


@pytest.fixture(scope="class")
def establish_audio_call():
    tc_teams_user = Base().tc_teams["user"]
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")

    pc_teams_ins.initial_call(tc_teams_user)
    time.sleep(5)
    tc_teams_room_ins.check_meeting_status("incoming_call")

    tc_teams_room_ins.accept_meeting_invite_request()
    time.sleep(10)
    tc_teams_room_ins.check_meeting_status("active_unmute")
    tc_teams_room_ins.turn_camera_off_in_meeting()

    yield
    tc_teams_room_ins.end_meeting()


@pytest.fixture(scope="function")
def turn_on_device_camera():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_user = Base().tc_teams["user"]

    if not pc_teams_ins.check_remote_camera_video_status("on", tc_teams_user):
        tc_teams_room_ins.turn_camera_on_in_meeting()


@pytest.fixture(scope="function")
def create_or_start_teams_call_via_ep():
    tc_teams_user = Base().tc_teams["user"]
    pc_teams_ins = init_apollo_teams_driver()
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_teams_ins.open()

    try:
        pc_teams_ins.check_call_status("active_unmute", tc_teams_user)
        tc_teams_room_ins.check_meeting_status("active_unmute")
        Logger.ins().std_logger().info("---> [TeamsConftest] Already exists teams meeting, no need create!!!")
    except:
        Logger.ins().std_logger().info("---> [TeamsConftest] No exists teams meeting,  create one!!!")
        # Cleanup existing call
        tc_teams_room_ins.cleanup_sp_meeting()
        pc_teams_ins.cleanup_sp_call()
        # Create new call from PC
        pc_teams_ins.initial_video_call(tc_teams_user)
        time.sleep(5)
        tc_teams_room_ins.check_meeting_status("incoming_call", timeout=15)
        tc_teams_room_ins.accept_meeting_invite_request()
        time.sleep(10)
        tc_teams_room_ins.check_meeting_status("active_unmute")


@pytest.fixture(scope="class")
def back_to_home():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    yield
    tc_teams_room_ins.open()


@pytest.fixture(scope="class")
def enable_bluetooth():
    enable_bluetooth_cmd = "svc bluetooth enable"
    pcos_ins = init_apollo_pcos_driver()
    vb_cmd_driver = CmdDriver(Base().vb_udid)

    pcos_ins.turn_on_bluetooth()
    vb_cmd_driver.exec_adb_shell_cmd(enable_bluetooth_cmd)


@pytest.fixture(scope="function")
def start_meeting_via_bluetooth_beaconing():
    tc_teams_user = Base().tc_teams["user"]
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    pc_ag_teams_ins.open()

    # Cleanup existing meeting
    tc_teams_room_ins.cleanup_sp_meeting()
    pc_ag_teams_ins.cleanup_sp_meeting()
    # Create new call from PC
    pc_ag_teams_ins.handle_meet_now().open()
    time.sleep(1)
    pc_ag_teams_ins.handle_meet_now().meet_now_with(esp_user=tc_teams_user)
    time.sleep(10)
    # By fw design: TC may take the phone call automatically while using bluetooth beaconing feature
    if Base().dut_name == "platform_gandalf":
        if not tc_teams_room_ins.is_sp_in_meeting():
            tc_teams_room_ins.check_meeting_status("incoming_call")
            tc_teams_room_ins.accept_meeting_invite_request()
    tc_teams_room_ins.check_meeting_status("active_unmute")
    pc_ag_teams_ins.check_meeting_status("audio_off")
    pc_ag_teams_ins.check_camera_status_in_meeting("off")


@pytest.fixture(scope="function")
def close_meet_now_page():
    pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    pc_ep_teams_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")

    yield
    pc_ag_teams_ins.handle_meet_now().close()
    pc_ep_teams_ins.handle_meet_now().close()


@pytest.fixture(scope="class")
def exit_chrome():
    kill_chrome_cmd = "taskkill /f /im chrome.exe"
    cmd_driver = CmdDriver()

    yield
    cmd_driver.exec_pcos_cmd(kill_chrome_cmd)


@pytest.fixture(scope="function")
def cancel_all_scheduled_meetings():
    pc_ag_teams = init_apollo_teams_driver("PC_AG_WIN")

    yield
    pc_ag_teams.cancel_scheduled_meeting()


@pytest.fixture(scope="function")
def recovery_vb_network():
    yield
    cmd_driver = CmdDriver(Base().vb_udid)
    cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")


@pytest.fixture(scope="function")
def recovery_tc_network():
    yield
    cmd_driver = CmdDriver(Base().tc_udid)
    cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")


@pytest.fixture(scope="function")
def recovery_tc_teams():
    yield
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    cmd_driver = CmdDriver(Base().tc_udid)
    cmd_driver.exec_adb_shell_cmd("am start -n com.microsoft.skype.teams.ipphone/com.microsoft.skype.teams.Launcher")
    tc_teams_room_ins.check_sp_status("home_ready")


@pytest.fixture(scope="function")
def recovery_vb_teams():
    yield
    vb_teams_room_ins = init_teams_room_driver(test_device="VB")
    cmd_driver = CmdDriver(Base().vb_udid)
    cmd_driver.exec_adb_shell_cmd("am start -n com.microsoft.skype.teams.ipphone/com.microsoft.skype.teams.Launcher")
    vb_teams_room_ins.check_sp_status("paired")


@pytest.fixture(scope="function")
def re_enable_proximity_join():
    tc_jabra_meeting_driver = TCJabraMeeting()
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")

    tc_teams_room_ins.goto_jabra_meeting()

    tc_jabra_meeting_driver.home_page().goto_admin()
    tc_jabra_meeting_driver.admin_page().goto_network_page()
    tc_jabra_meeting_driver.network_page().goto_bluetooth()
    # Turn off "Proximity Join", Verify the settings reflect on the device
    tc_jabra_meeting_driver.network_page().set_proximity_join("off")
    time.sleep(3)
    tc_jabra_meeting_driver.network_page().check_proximity_join("off")

    # Turn on "Proximity Join", Verify the setting reflect on the device
    tc_jabra_meeting_driver.network_page().set_proximity_join("on")
    time.sleep(3)
    tc_jabra_meeting_driver.network_page().check_proximity_join("on")

    tc_teams_room_ins.open()

