import pytest
from apollo_base.cmd_driver import CmdDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver

from testcase.base import Base


@pytest.fixture(scope="class", autouse=True)
def open_kiosk_mode():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_cmd_driver = CmdDriver(Base().tc_udid)
    pcos_ins = init_apollo_pcos_driver()
    if str(tc_cmd_driver.exec_adb_shell_cmd("getprop persist.jabra.kiosk.mode")).strip() == "0":
        tc_cmd_driver.exec_adb_shell_cmd("setprop persist.jabra.kiosk.mode 1")
        tc_cmd_driver.exec_adb_shell_cmd("reboot", check=False)
        pcos_ins.wait_device_pid_ready(Base().tc_vid, 90, Base().tc_pid)
        tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        tc_teams_room_ins.check_sp_status("home_ready")


@pytest.fixture(scope="class", autouse=True)
def close_kiosk_mode():
    yield
    pcos_ins = init_apollo_pcos_driver()
    tc_cmd_driver = CmdDriver(Base().tc_udid)
    tc_cmd_driver.exec_adb_shell_cmd("setprop persist.jabra.kiosk.mode 0")
    tc_cmd_driver.exec_adb_shell_cmd("reboot", check=False)
    pcos_ins.wait_device_pid_ready(Base().tc_vid, 90, Base().tc_pid)
    tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
