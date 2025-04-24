import pytest, time
from apollo_base.cmd_driver import CmdDriver
from apollo_teams_room.driver import init_teams_room_driver
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.Teams_Console_Certification_v3 import *
from tools.script.jama_test_case.firefoot.Teams_Console_Certification_v3 import *
from testcase.base import Base


@pytest.mark.usefixtures("back_to_home")
@pytest.mark.feat_teams_console_device_settings
@pytest.mark.feat_teams_console_camera_shutter
class TestFeatTeamsConsoleDeviceCameraShutter(Base):

    def setup_class(self):
        self.vb_cmd_driver = CmdDriver(Base().vb_udid)
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.tc_teams_room_ins.open()

    @pytest.mark.gandalf_nightly
    # 6.7 [Camera shutter] Verify Camera shutter intent
    @jama_tc(Gan_TC_ESW_44829, Fif_TC_ESW_110060)
    def test_camera_shutter_intent(self):
        if self.dut_name == "platform_firefoot":
            pytest.skip("BUG 28850:  FF does not have a hardware camera shutter")
        cmd = '''settings get system "android.settings.CAMERA_COVER_STATUS"'''
        assert int(str(self.vb_cmd_driver.exec_adb_shell_cmd(cmd)).strip().replace("\n", "")) == 1

    @pytest.mark.gandalf_nightly
    @pytest.mark.firefoot_nightly
    # 6.7 [Mic Switch] Verify mic switch status intent
    @jama_tc(Gan_TC_ESW_44830, Fif_TC_ESW_110061)
    def test_verify_mic_switch_status_intent(self, cleanup_tc_teams_call):
        # init meeting
        self.tc_teams_room_ins.initial_meeting()
        time.sleep(10)
        assert self.tc_teams_room_ins.is_sp_in_meeting()
        self.tc_teams_room_ins.mute_meeting()

        # Mute meeting
        time.sleep(5)
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep calling:CallActions| grep mute | tail -1")
        assert "mute state to true" in rst

        # Unmute meeting
        self.tc_teams_room_ins.unmute_meeting()
        time.sleep(5)
        rst = self.vb_cmd_driver.exec_adb_shell_cmd("logcat -d | grep calling:CallActions | grep mute | tail -1")
        assert "mute state to false" in rst
