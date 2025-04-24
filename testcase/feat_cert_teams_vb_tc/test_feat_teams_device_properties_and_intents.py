import pytest, time
from apollo_base.cmd_driver import CmdDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.systemlogger import Logger
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.feat_teams_device_properties_and_intents
class TestFeatTeamsDevicePropertiesAndIntents(Base):

    def setup_class(self):
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.pcos_ins = init_apollo_pcos_driver()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44073, Gan_TC_ESW_44074, Gan_TC_ESW_44075, Gan_TC_ESW_44079, Fif_TC_ESW_110080, Fif_TC_ESW_110081, Fif_TC_ESW_110082, Fif_TC_ESW_110086)
    def test_device_properties(self):
        cmd_get_fw_ver = "getprop build.firmware.version"
        cmd_get_teams_device_type = "settings get secure teams_device_type"
        cmd_get_teams_device_capabilities = "settings get secure teams_device_capabilities"
        cmd_get_build = "getprop | grep ro.build"
        # Check TC & VB Firmware Version
        vb_fw_ver = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_fw_ver)
        vb_version = self.vb_cmd_driver.exec_adb_shell_cmd("version")
        assert vb_fw_ver in vb_version, f"Check VB FW Version Failed, {vb_fw_ver}"
        tc_fw_ver = self.tc_cmd_driver.exec_adb_shell_cmd(cmd_get_fw_ver)
        tc_version = self.tc_cmd_driver.exec_adb_shell_cmd("version")
        assert tc_fw_ver in tc_version, f"Check TC FW Version Failed, {tc_fw_ver}"

        # Check Device Type
        vb_type = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_teams_device_type)
        assert vb_type.strip() == "norden", f"Check VB Teams Device Type Failed, {vb_type}"
        tc_type = self.tc_cmd_driver.exec_adb_shell_cmd(cmd_get_teams_device_type)
        assert tc_type.strip() == "nordenConsole", f"Check TC Teams Device Type Failed, {tc_type}"

        # Check Device Capabilities
        vb_capa = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_teams_device_capabilities)
        Logger.ins().std_logger().info(f"Teams Device Capabilities get from VB: {vb_capa}")
        assert "video" in vb_capa, f"Check 'video' in VB Teams Device Capabilities Failed"
        assert "hdmi_content_sharing" in vb_capa, f"Check 'hdmi_content_sharing' in VB Teams Device Capabilities Failed"
        assert "console_pairing" in vb_capa, f"Check 'console_pairing' in VB Teams Device Capabilities Failed"
        # For Firefoot. it only support single display so skip this check
        if self.dut_name == "platform_gandalf":
            assert "multiple_displays" in vb_capa, f"Check 'multiple_displays' in VB Teams Device Capabilities Failed"

        tc_capa = self.tc_cmd_driver.exec_adb_shell_cmd(cmd_get_teams_device_capabilities)
        Logger.ins().std_logger().info(f"Teams Device Capabilities get from TC: {tc_capa}")
        assert "console_pairing" in vb_capa, f"Check 'console_pairing' in TC Teams Device Capabilities Failed"

        # Check Firmware for production should be released signed
        # Note that user-debug version is "test-keys", use version is "release-keys"
        vb_build = self.vb_cmd_driver.exec_adb_shell_cmd(cmd_get_build)
        assert "[ro.build.keys]: [test-keys]" in vb_build, f"Check VB FW signed Failed, {vb_build}"
        tc_build = self.tc_cmd_driver.exec_adb_shell_cmd(cmd_get_build)
        assert "[ro.build.tags]: [dev-keys]" in tc_build, f"Check TC FW signed Failed, {tc_build}"

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44022, Fif_TC_ESW_110079)
    def test_webview_version(self):
        # This command reply something like versionName=121.0.6167.205
        webview_ver = self.tc_cmd_driver.exec_adb_shell_cmd("dumpsys package com.android.webview | grep versionName").strip().replace("versionName=", "")
        webview_main_ver = webview_ver.split(".")[0]
        assert int(webview_main_ver) >= 69, f"The webview version is {webview_ver}, which is less than 69. Please update the webview to the latest version."

    @jama_tc(Gan_TC_ESW_44076, Gan_TC_ESW_44077, Fif_TC_ESW_110083, Fif_TC_ESW_110084)
    def test_device_intents_data(self):
        self.tc_cmd_driver.exec_adb_cmd("logcat -c")
        self.vb_cmd_driver.exec_adb_cmd("logcat -c")
        # Reboot TC to make sure at least once pair in logs
        self.tc_cmd_driver.exec_adb_cmd("reboot")
        time.sleep(10)
        # wait device ready
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.tc_teams_room_ins.check_sp_status("home_ready")

        # Get VB IP and Mac Address
        vb_ip_addr = self.vb_cmd_driver.exec_adb_shell_cmd("ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1").strip().split("\n")[0]
        vb_mac_addr = self.vb_cmd_driver.exec_adb_shell_cmd("cat /sys/class/net/eth0/address").strip().replace(":", "-").upper()
        # Get Teams Pair Intent Data
        pair_intent_data = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT").strip()
        assert f'"roomDeviceIPAddress":"{vb_ip_addr}"' in pair_intent_data, f"VB IP Address {vb_ip_addr} not found in Teams Pair Intent Data"
        assert f'"roomDeviceMACAddress":"{vb_mac_addr}"' in pair_intent_data, f"VB Mac Address {vb_mac_addr} not found in Teams Pair Intent Data"

        ack_data = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT-TeamsPairAckIntentData | grep com.microsoft.skype.teams.console.action.ack", timeout=30).strip()
        assert ack_data != "", "Teams Pair Ack Intent Data not found"
        result_data = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT-TeamsPairResultIntentData | grep com.microsoft.skype.teams.console.action.result", timeout=30).strip()
        assert result_data != "", "Teams Pair Result Intent Data not found"

        # Check pairing status
        pair_action = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT | grep actionName | grep pair", timeout=30).strip()
        assert "actionName = pair" in pair_action, "Pairing action is not pair in Teams Pair Intent Data"

        pairing_status = self.tc_cmd_driver.exec_adb_shell_cmd("logcat -d | grep NordenFirmwarePairingManager", timeout=30).strip()
        assert "OEM command: pair complete, result: success" in pairing_status, "Pairing status is not success in Teams Pair Intent Data"

        vb_oem_action = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep JABRA_PARTNER_AGENT-TeamsPairingStatusUpdatedIntentData | grep pairingStatus=paired", timeout=30).strip()
        assert vb_oem_action != "", "pairingStatus not found in VB Teams Pairing Status Updated Intent Data"

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44834, Fif_TC_ESW_110087)
    def test_battery_optimization_disable(self):
        battery_info = self.tc_cmd_driver.exec_adb_shell_cmd("dumpsys deviceidle | grep mDeepEnabled").strip()
        assert "mDeepEnabled=false" in battery_info, "Battery Optimization is not disabled"
