import pytest, time
from apollo_jabra.tc_jabra_meeting_driver.installation_flow_page import InstallationFlowPage
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_base.gnp_private_driver import GnpPrivateDriver
from testcase.base import Base
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *


@pytest.mark.feat_teams_console_device_settings_after_qfil
class TestFeatTeamsConsoleDevicesSettingsAfterQFIL(Base):

    def setup_class(self):
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.gnp_ins = GnpPrivateDriver()
        self.pcos_ins = init_apollo_pcos_driver()
        self.tc_jose_api_ins = JoseApiDriver(test_device="TC")
        self.tc_installation_flow = InstallationFlowPage(Base().tc_udid)
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44052, Gan_TC_ESW_44021, Fif_TC_ESW_110041, Fif_TC_ESW_110005)
    def test_select_service_provider_after_factory_reset(self):
        # Factory reset TC and VB
        self.gnp_ins.gnp_write(self.tc_pid, "01", "13", "11", ["00"])
        self.gnp_ins.gnp_write(self.vb_pid, "01", "13", "11", ["00"])
        time.sleep(5)
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.pcos_ins.wait_device_pid_ready(self.vb_vid, 90, self.vb_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.vb_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        time.sleep(20)
        set_pre_vaas_cmds = ["cd system/vendor/bin", "./jose_service_controller storage -w preselected.vaasprovider:string:TEAMS"]
        check_pre_vaas_cmds = ["cd system/vendor/bin", "./jose_service_controller storage -r preselected.vaasprovider"]

        self.vb_cmd_driver.exec_adb_shell_cmd(set_pre_vaas_cmds)
        assert self.vb_cmd_driver.exec_adb_shell_cmd(check_pre_vaas_cmds).find("TEAMS") > 0, "#pre_condition check pre-vaas as Teams fail"

        try:
            self.tc_installation_flow.common_flow()
        except:
            pass
        self.tc_installation_flow.connect_to_devices(Base().tc_pair_udid)
        self.tc_installation_flow.click_next_button()
        self.tc_installation_flow.skip_update_firmware_page()
        self.tc_installation_flow.skip_jabraplus_page()
        self.tc_installation_flow.accept_microsoft_privacy()
        self.tc_teams_room_ins.check_sp_status("vaas_ready")
        # Verify DUT settings transferred to Touch Console Settings page.
        self.vb_teams_room_ins.check_sp_status("vaas_ready")


@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_device_settings_device_settings
class TestFeatTeamsConsoleDevicesSettings(Base):
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.pcos_ins = init_apollo_pcos_driver()

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    @jama_tc(Gan_TC_ESW_44808, Fif_TC_ESW_110007)
    @pytest.mark.usefixtures("cleanup_tc_teams_call")
    def test_service_provider_not_ask_to_change_after_reboot(self):
        # 1.Reboot TC
        self.tc_cmd_driver.exec_adb_cmd("reboot")
        self.pcos_ins.wait_device_pid_ready(self.tc_vid, 90, self.tc_pid)
        self.tc_cmd_driver.exec_adb_cmd_wait_output(r"logcat -d -b events| grep boot_progress_enable_screen", 200)
        self.tc_teams_room_ins.check_sp_status("home_ready")
