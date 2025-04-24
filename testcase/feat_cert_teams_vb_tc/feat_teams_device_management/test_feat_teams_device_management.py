import json

import pytest, time
from apollo_base.decorate import jama_tc
from apollo_base.systemlogger import Logger
from apollo_gn_android.driver import GnAndroidNoUIDriver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_web.web_tac_driver import WebTacDriver
from apollo_pcos.driver import init_apollo_pcos_driver
import concurrent.futures

from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


"""
2020-08-21 Remove following test cases and labeling [M] to relevant Jama testcases due to:
1. It's not legal behavior to factory reset without sign out Teams account
2. It's complex if we would like to add sign out logic before sign in

@pytest.mark.feat_teams_console_device_management_after_qfil
class TestFeatTeamsConsoleDeviceManagementAfterQFIL(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.vb_cmd_driver = CmdDriver(Base().tc_udid)

    # @jama_tc(Gan_TC_ESW_43988, Gan_TC_ESW_44006)
    @jama_tc(Gan_TC_ESW_44006,Gan_TC_ESW_43988)
    def test_check_tc_vb_admin_agent_log_after_sign_in(self, factory_reset_then_pair_tc_vb):
        # login and repair
        self.tc_cmd_driver.exec_adb_shell_cmd('logcat -c')
        self.vb_cmd_driver.exec_adb_shell_cmd('logcat -c')

        # VB login and repair
        self.vb_teams_room_ins.login()
        self.vb_teams_room_ins.check_sp_status("home_ready")

        # TC login and repair
        self.tc_teams_room_ins.login()
        self.tc_teams_room_ins.check_sp_status("home_ready")

        time.sleep(100)
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d -s EnrollRequestHandler")
        assert "userId" in rst
        assert "model='panacasttc'" in rst
        assert "manufacturer='jabra'" in rst
        assert f"uniqueId='{Base().tc_udid}'" in rst
        assert f"oemSerialNumber=\'{Base().tc_udid}\'" in rst

        rst = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d -s EnrollRequestHandler")
        assert "userId" in rst
        assert "model='panacasttc'" in rst
        assert "manufacturer='jabra'" in rst
        assert f"uniqueId='{Base().tc_udid}'" in rst
        assert f"oemSerialNumber=\'{Base().tc_udid}\'" in rst
"""


# @pytest.mark.usefixtures("exit_chrome")
@pytest.mark.feat_teams_device_management
class TestFeatTeamsConsoleDeviceManagement(Base):
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.web_tac_driver = WebTacDriver()
        self.pcos_ins = init_apollo_pcos_driver()
        self.tac_display_id = Base().tc_pair_udid
        self.tc_gn_android_ins = GnAndroidNoUIDriver(Base().tc_udid)
        self.vb_gn_android_ins = GnAndroidNoUIDriver(Base().vb_udid)

    def __test_heartbeat(self, cmd_driver, vid, pid, software_version: dict, ip):
        # Check if the heartbeat mechanism is working, and check again after TC reboot
        for i in range(2):
            cmd_agent_repo = "logcat -d | grep AgentRepository | grep cookie| tail -1"

            ret1 = cmd_driver.exec_adb_cmd_wait_output(cmd_agent_repo, 180)
            cmd_driver.exec_adb_shell_cmd("logcat -c", check=False)
            time.sleep(180)
            ret2 = cmd_driver.exec_adb_cmd_wait_output(cmd_agent_repo, 180)

            # Fix issue sometimes it's new minute, need to plus 60
            if int(ret2[9:11]) > int(ret1[9:11]):
                interval = int(ret2[9:11]) - int(ret1[9:11])
            else:
                interval = int(ret2[9:11]) + 60 - int(ret1[9:11])
            # Verify HeartBeat Interval, sometimes it's 2 mins, sometimes it's 3 mins
            assert interval in [2, 3, 4, 6], f"Heart Beat Interval is not 2 min or 3 mins!!! \n{ret1}\n{ret2}"

            agent_repo_dict = json.loads(ret2.split("AgentRepository: ")[-1])
            # Verify HeartBeat provide IP
            assert "ipAddress" in agent_repo_dict.keys(), "Check IP Address in HeartBeat Failed !!"
            assert agent_repo_dict.get("ipAddress") == ip, "Check IP Address in HeartBeat Failed !!"

            # Verify HeartBeat provide software version
            for key in software_version.keys():
                if key != "companyPortalVersionName" or key != "companyPortalVersion":
                    assert key in agent_repo_dict.keys(), f"Check {key} in HeartBeat Failed !!"
                    assert software_version.get(key) in agent_repo_dict.keys(), f"Check {key}'s value in HeartBeat Failed !!"

            cmd_driver.exec_adb_shell_cmd("logcat -c", check=False)

            if i == 0:
                cmd_driver.exec_adb_shell_cmd("logcat -c", check=False)
                cmd_driver.exec_adb_cmd("reboot")
                self.pcos_ins.wait_device_pid_ready(vid, 120, pid)
                cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
                time.sleep(10)

    @pytest.mark.timeout(700)
    @jama_tc(Gan_TC_ESW_43989, Gan_TC_ESW_44007, Gan_TC_ESW_44008, Gan_TC_ESW_44001, Fif_TC_ESW_109970, Fif_TC_ESW_109988, Fif_TC_ESW_109989, Fif_TC_ESW_109982)
    def test_heartbeat(self):
        self.tc_software_version = self.tc_gn_android_ins.get_installed_packages_versions()
        self.vb_software_version = self.vb_gn_android_ins.get_installed_packages_versions()
        self.tc_ip = self.tc_gn_android_ins.get_ip_address()
        self.vb_ip = self.vb_gn_android_ins.get_ip_address()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tc_heartbeat = executor.submit(self.__test_heartbeat, self.tc_cmd_driver, self.tc_vid, self.tc_pid, self.tc_software_version, self.tc_ip)
            vb_heartbeat = executor.submit(self.__test_heartbeat, self.vb_cmd_driver, self.vb_vid, self.vb_pid, self.vb_software_version, self.vb_ip)

            concurrent.futures.wait([tc_heartbeat, vb_heartbeat])

    @pytest.mark.timeout(300)
    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43992, Fif_TC_ESW_109973)
    def test_admin_portal_device_inventory_show_the_current_user_signed(self):
        # Click the user name displayed in the device entry
        self.web_tac_driver.open_devices_collaboration_bars()

        # 	Verify that the user page in the admin portal opens
        self.web_tac_driver.check_username_in_devices_collaboration_bars(Base().tc_teams["user"])
        self.web_tac_driver.check_status_in_devices_collaboration_bars("Healthy", "Non-urgent")

        # Click the user name displayed in the device entry
        self.web_tac_driver.open_devices_collaboration_bars("VB")

        # 	Verify that the user page in the admin portal opens
        self.web_tac_driver.check_username_in_devices_collaboration_bars(Base().vb_teams["user"])
        self.web_tac_driver.check_status_in_devices_collaboration_bars("Healthy", "Non-urgent")

    @pytest.mark.timeout(300)
    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_43994, Fif_TC_ESW_109975)
    def test_admin_portal_display_sw_vers(self):
        cmd_agent_repo = "cat /data/log/logcat.log | grep AgentRepository | grep cookie | tail -1"

        # Get SW version from Agent heartbeat to TAC within 2 mins
        ret = self.vb_cmd_driver.exec_adb_cmd_wait_output(cmd_agent_repo, 120)

        agent_sw_ver = json.loads(ret.split("AgentRepository: ")[-1])["softwareVersions"]
        Logger.ins().std_logger().info(f"Get agent_sw_ver={agent_sw_ver}")

        # Get SW version from TAC
        tac_sw_ver = self.web_tac_driver.get_device_health_data(self.tac_display_id)
        # self.web_tac_driver.quit()
        Logger.ins().std_logger().info(f"Get tac_sw_ver={tac_sw_ver}")
        assert tac_sw_ver is not None, "Sofware Version is None in TAC"

        # Verify SW version between TAC and Agent
        assert tac_sw_ver["Teams Admin Agent"] == agent_sw_ver["adminAgentVersionName"], "Check Teams Admin Agent Failed"
        assert tac_sw_ver["Firmware"] == agent_sw_ver["osVersionName"], "Check Firmware Failed"
        # For MDEP, the solution is changed to ngms, so there is no Company Portal App
        android_ver = self.vb_cmd_driver.exec_adb_shell_cmd("getprop ro.build.version.release")
        if android_ver == "10":
            assert tac_sw_ver["Company Portal App"] == agent_sw_ver["companyPortalVersionName"], "Check Company Portal App Failed"
        assert tac_sw_ver["OEM Agent"] == agent_sw_ver["oemAgentVersionName"], "Check OEM Agent App Failed"
        assert tac_sw_ver["Teams"] == agent_sw_ver["teamsAppVersionName"], "Check Teams App Failed"
