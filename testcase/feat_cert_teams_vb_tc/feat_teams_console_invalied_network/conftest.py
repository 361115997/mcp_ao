import time

import pytest
from apollo_base.cmd_driver import CmdDriver
from apollo_base.gnp_private_driver import GnpPrivateDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_teams_room.driver import init_teams_room_driver

from testcase.base import Base


@pytest.fixture(scope="function")
def factory_reset_then_pair_tc_vb():
    gnp_ins = GnpPrivateDriver()
    pcos_ins = init_apollo_pcos_driver()
    tc_cmd_driver = CmdDriver(Base().tc_udid)
    vb_cmd_driver = CmdDriver(Base().vb_udid)
    tc_jose_api_ins = JoseApiDriver(test_device="TC")
    gnp_ins.gnp_write(Base().tc_pid, "01", "13", "11", ["00"])
    gnp_ins.gnp_write(Base().vb_pid, "01", "13", "11", ["00"])

    time.sleep(5)
    pcos_ins.wait_device_pid_ready(Base().tc_vid, 90, Base().tc_pid)
    pcos_ins.wait_device_pid_ready(Base().vb_vid, 90, Base().vb_pid)
    tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
    vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
    # Need to close build-in keyboard to use nico keyboard

    tc_jose_api_ins.pair_active_device(Base().tc_pair_udid)
    # Set VaaS as Teams and Launch Teams app
    tc_jose_api_ins.vaas_settings_set_provider_teams()
    tc_jose_api_ins.launch_vaas_services()


@pytest.fixture(scope="function")
def cleanup_sp_meeting():
    yield
    ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    tc_teams_ins = init_teams_room_driver(test_device="TC")

    ag_teams_ins.cleanup_sp_meeting()
    tc_teams_ins.cleanup_sp_meeting()


@pytest.fixture(scope="function")
def cleanup_sp_call():
    yield
    ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    tc_teams_ins = init_teams_room_driver(test_device="TC")

    ag_teams_ins.cleanup_sp_call()
    tc_teams_ins.cleanup_sp_meeting()


@pytest.fixture(scope="function")
def recovery_tc_teams():
    yield
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_teams_room_ins.adb_utils.app_switch()
    time.sleep(2)
    tc_teams_room_ins.adb_utils.app_switch()
    time.sleep(2)
    tc_teams_room_ins.adb_utils.app_switch()
    time.sleep(2)
    tc_teams_room_ins.adb_utils.app_switch()


@pytest.fixture(scope="function")
def recovery_vb_teams():
    yield
    tc_teams_room_ins = init_teams_room_driver(test_device="VB")
    tc_teams_room_ins.adb_utils.switch_app()
    time.sleep(5)
    tc_teams_room_ins.adb_utils.switch_app()
    time.sleep(5)
    tc_teams_room_ins.adb_utils.switch_app()
    time.sleep(5)
    tc_teams_room_ins.adb_utils.switch_app()


@pytest.fixture(scope="function")
def tc_back():
    yield
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_teams_room_ins.adb_utils.back()


@pytest.fixture(scope="function")
def recovery_vb_network():
    yield
    cmd_driver = CmdDriver(Base().vb_udid)
    cmd_driver.exec_adb_shell_cmd("ifconfig eth0 up")


@pytest.fixture(scope="function")
def cancel_scheduled_meeting():
    yield
    ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
    ag_teams_ins.cancel_scheduled_meeting()
