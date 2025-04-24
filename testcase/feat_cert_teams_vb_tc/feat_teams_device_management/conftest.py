import time

import pytest
from apollo_base.cmd_driver import CmdDriver
from apollo_base.gnp_private_driver import GnpPrivateDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_web.web_gandalf_teams_driver import WebGandalfTeamsDriver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from testcase.base import Base


@pytest.fixture(scope="class")
def exit_chrome():
    kill_chrome_cmd = "taskkill /f /im chrome.exe"
    cmd_driver = CmdDriver()

    yield
    cmd_driver.exec_pcos_cmd(kill_chrome_cmd)


@pytest.fixture(scope="class")
def login_teams():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    vb_teams_room_ins = init_teams_room_driver(test_device="VB")
    tc_cmd_driver = CmdDriver(Base().tc_udid)
    vb_cmd_driver = CmdDriver(Base().vb_udid)
    tc_jose_api_ins = JoseApiDriver(test_device="TC")
    gnp_ins = GnpPrivateDriver()
    pcos_ins = init_apollo_pcos_driver()
    web_ins = WebGandalfTeamsDriver()
    try:
        tc_teams_room_ins.open()
        tc_teams_room_ins.check_sp_status("home_ready")
    except:
        # Factory reset TC and VB
        # gnp_ins.gnp_write(Base().tc_pid, "01", "13", "11", ["00"])
        # gnp_ins.gnp_write(Base().vb_pid, "01", "13", "11", ["00"])
        # time.sleep(5)
        # pcos_ins.wait_device_pid_ready(Base().tc_vid, 90, Base().tc_pid)
        # pcos_ins.wait_device_pid_ready(Base().vb_vid, 90, Base().vb_pid)
        # tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        # vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        # pair TC and VB from TC via JoseApiExample APP
        tc_jose_api_ins.pair_active_device(Base().tc_pair_udid)
        # Set VaaS as Teams and Launch Teams app
        tc_jose_api_ins.vaas_settings_set_provider_teams()
        tc_jose_api_ins.launch_vaas_services()
        tc_teams_room_ins.check_sp_status("vaas_ready")
        vb_teams_room_ins.check_sp_status("vaas_ready")

        vb_login_code = vb_teams_room_ins.get_web_login_code()
        web_ins.login_teams(vb_login_code)
        time.sleep(60)
        vb_teams_room_ins.check_sp_status("home_ready")
        # Login TC from web
        tc_login_code = tc_teams_room_ins.get_web_login_code()
        web_ins.login_teams(tc_login_code)
        time.sleep(60)
        tc_teams_room_ins.check_sp_status("home_ready")
        # Wait for TC and VB to be paired
        vb_teams_room_ins.check_sp_status("paired")


@pytest.fixture(scope="class")
def yield_set_configure_exit_test():
    yield
    from apollo_web.web_tac_driver import WebTacDriver

    web_tac_driver = WebTacDriver()
    web_tac_driver.apply_configuration_profiles_to_devices("ApolloExitTesting")
    kill_chrome_cmd = "taskkill /f /im chrome.exe"
    cmd_driver = CmdDriver()
    cmd_driver.exec_pcos_cmd(kill_chrome_cmd)
