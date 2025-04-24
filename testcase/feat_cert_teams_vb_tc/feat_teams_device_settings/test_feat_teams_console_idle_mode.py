import pytest, time
from apollo_teams.driver import init_apollo_teams_driver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.cmd_driver import CmdDriver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_idle_mode
class TestFeatTeamsConsoleIdleMode(Base):

    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.pc_ag_teams_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.teams_tc_user = Base().tc_teams["user"]  # "gnlabauto03@jabralab.onmicrosoft.com"

        self.tc_cmd_driver = CmdDriver(Base().tc_udid)
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)

        self.tc_jabra_meeting_driver = TCJabraMeeting()

    @jama_tc(Gan_TC_ESW_44055, Gan_TC_ESW_43888, Fif_TC_ESW_110052, Fif_TC_ESW_109869)
    def test_idle_mode_in_tc(self, teams_start_tc_jabra_meeting_setting, resets_the_screen_timeout):
        # set device screen off timeout as 60s
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_video_page()
        self.tc_jabra_meeting_driver.video_page().goto_monitor()
        self.tc_jabra_meeting_driver.video_page().set_standby_interval("60")
        self.tc_jabra_meeting_driver.video_page().goto_camera()

        # Wait 63, Check if the screen is on standby
        time.sleep(70)

        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Asleep" in rst

        # wait some seconds for syncing settings to VB
        time.sleep(5)
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Asleep" in rst or "mWakefulness=Dozing" in rst

        # Unlock screen, Check if the screen is wake up
        self.tc_teams_room_ins.adb_utils.unlock()
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Awake" in rst

        self.vb_teams_room_ins.adb_utils.unlock()
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Awake" in rst

    @jama_tc(Gan_TC_ESW_44056, Fif_TC_ESW_110053)
    @pytest.mark.usefixtures("cleanup_teams_meeting_in_func", "back_to_home_in_func")
    def test_idle_mode_will_reset_after_incoming_call(self, teams_start_tc_jabra_meeting_setting,
                                                      resets_the_screen_timeout):
        # set device screen off timeout as 60
        self.tc_jabra_meeting_driver.home_page().goto_admin()
        self.tc_jabra_meeting_driver.admin_page().goto_video_page()
        self.tc_jabra_meeting_driver.video_page().goto_monitor()
        self.tc_jabra_meeting_driver.video_page().set_standby_interval("60")
        self.tc_jabra_meeting_driver.video_page().goto_camera()
        # Need go back to Teams home page to accept meeting invite
        self.tc_teams_room_ins.open()

        # Wait 10s, Make an incoming call from PC
        time.sleep(10)
        self.pc_ag_teams_ins.initial_meeting()
        self.pc_ag_teams_ins.invite_people_into_meeting(self.teams_tc_user)

        # The device screen should turn on for incoming calls, and the screen timeout should reset.
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Awake" in rst

        # Confirm with manual QA: can workaround by accepting meeting on TC then leave
        self.tc_teams_room_ins.check_meeting_status(status="incoming_call", timeout=20)
        self.tc_teams_room_ins.accept_meeting_invite_request()
        self.tc_teams_room_ins.leave_meeting()

        # The screen should not turn off after 50 seconds.
        time.sleep(50)
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Awake" in rst

        rst = self.vb_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Awake" in rst

        # The screen should turn off after waiting for 13 seconds.
        time.sleep(13)
        rst = self.tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Asleep" in rst

        # Confirmed with manual QA: need to wait some time to sync between TC and VB
        time.sleep(15)
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep mWakefulness""")
        assert "mWakefulness=Asleep" in rst or "mWakefulness=Dozing" in rst
