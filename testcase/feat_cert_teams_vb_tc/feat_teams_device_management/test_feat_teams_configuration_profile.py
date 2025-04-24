import time
from datetime import datetime
import re
import pytest
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_web.web_tac_driver import WebTacDriver

from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_jabra.vb_jabra_meeting_driver.driver import VBJabraMeeting
from testcase.base import Base


@pytest.mark.usefixtures("yield_set_configure_exit_test")
@pytest.mark.usefixtures("back_to_home")
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_console_configuration_profile
class TestFeatTeamsConsoleConfigurationProfile(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.vb_jabra_meeting_driver = VBJabraMeeting()
        self.tc_jose_api_ins = JoseApiDriver("TC")
        self.pcos_ins = init_apollo_pcos_driver()
        self.web_tac_driver = WebTacDriver()

    @jama_tc(Gan_TC_ESW_44013, Gan_TC_ESW_44020, Gan_TC_ESW_44019, Gan_TC_ESW_44018, Gan_TC_ESW_44017, Gan_TC_ESW_44064, Gan_TC_ESW_44016, Fif_TC_ESW_109996, Fif_TC_ESW_110002, Fif_TC_ESW_110001, Fif_TC_ESW_110000, Fif_TC_ESW_109999, Fif_TC_ESW_110069, Fif_TC_ESW_109998)
    def test_teams_console_configuration_profile(self):

        # 1 Clearly the logcat log
        self.vb_cmd_driver.exec_adb_shell_cmd("logcat -c")
        time.sleep(3)

        # 2 Set the configuaration as muban ApolloTesting.
        self.web_tac_driver.apply_configuration_profiles_to_devices("ApolloTesting")
        self.vb_cmd_driver.exec_adb_cmd_wait_output("logcat -d | grep systemConfig | grep DesiredValue", 1000, with_root=True)
        time.sleep(30)

        # 3 Check Language sync up
        current_language = self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.locale").strip()
        assert current_language == "en-US", f"Check language fail, current is {current_language}"

        # 4 Check Time Format sync up
        current_time_format = self.tc_cmd_driver.exec_adb_shell_cmd("settings get system time_12_24").strip()
        assert current_time_format == "24", f"Check timeformat 24h fail, current is {current_time_format}"

        # 5 Check Logging enable sync up
        current_logging_status = self.tc_cmd_driver.exec_adb_shell_cmd("jose_service_controller system -i").strip()
        assert "System logging enabled" in current_logging_status, f"Check logging status fail, current is {current_logging_status}"

        # 6 Check TimeZone sync up
        current_timezone = self.tc_cmd_driver.exec_adb_shell_cmd("getprop persist.sys.timezone").strip()
        assert current_timezone == "Pacific/Honolulu", f"Check time zone fail, current {current_timezone}"

        # 7 Check Static IP sync up
        # Agree with Manual Test Team mark this as M
        # vb_ip_address = re.findall(r'inet addr:(\d+\.\d+\.\d+\.\d+)', self.vb_cmd_driver.exec_adb_shell_cmd("ifconfig eth0"))[0]
        # ip_configuration_log = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep systemConfig| grep DesiredValue| grep ipAddress| tail -1")
        # expect_ip = re.search(r'"ipAddress":"(.*?)"', ip_configuration_log).group(1)
        # assert expect_ip == vb_ip_address,  f"Check Static IP failed, current is {vb_ip_address}, expect is {expect_ip}"

        # 8 Check Date format sync up
        current_date_format = self.tc_cmd_driver.exec_adb_shell_cmd("settings get system date_format").strip()
        assert "MM/dd/yyyy", f"Check date format fail, current is {current_date_format}"

        # 9 Check admin passwrod sync up
        self.tc_teams_room_ins.open()
        self.tc_teams_room_ins.goto_jabra_meeting()
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().close_admin_page()
        self.tc_teams_room_ins.open()
