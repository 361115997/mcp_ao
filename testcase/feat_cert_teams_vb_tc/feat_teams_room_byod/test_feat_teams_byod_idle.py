import pytest, time
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.BYOD import *
from testcase.base import *
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_teams_room.driver import init_teams_room_driver
from apollo_swb.driver import init_swb_driver
from apollo_pcos.driver import init_apollo_pcos_driver
from testcase.base import Base
from apollo_base.cmd_driver import CmdDriver


@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_byod_idle
class TestFeatTeamsIdle:
    def setup_class(self):
        self.tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        self.vb_teams_room_ins = init_teams_room_driver(test_device="VB")
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.dut_name = Base().dut_name
        self.pcos_ins = init_apollo_pcos_driver()
        self.dut_audio_pid = Base().dut.get("dut_audio_pid")
        self.dut_video_pid = Base().dut.get("dut_video_pid")
        self.gn_vid = Base().dut.get("dut_gn_vid")
        self.cmd_driver = CmdDriver()
        self.swb_usb = init_swb_driver(Base().swb_ctrl_unit)
        os.environ["current_vaas"] = "Teams"

    @pytest.mark.usefixtures("yield_swb_usb_connect")
    @jama_tc(Gan_TC_ESW_51375, Gan_TC_ESW_40207)
    def test_end_byod_mode_by_unplug(self):
        # 1 Go to Device Manager of PC, UVC and UAC devices should be listed in it.
        time.sleep(10)
        stream = self.cmd_driver.exec_pcos_cmd(f"wmic path CIM_LogicalDevice get DeviceID|findstr {self.gn_vid} | findstr 30")
        assert self.dut_audio_pid in stream, "Check {self.dut_audio_pid} appear fail"
        assert self.dut_video_pid in stream, "Check {self.dut_video_pid} appear fail"

        # 2 Unplug the USB cable, VB and TC return teams room page
        self.swb_usb.disconn_dut_from_apollo(self.dut_name)
        time.sleep(60)
        self.tc_teams_room_ins.check_sp_status("home_ready")

        # 3 Go to Device Manager of PC, UVC and UAC devices should be NOT listed in it.
        # UAC device: Echo Cancelling Speakerphone (Jabra PanaCast 50 VBS) (0b0e:3042)
        # UVC device: Jabra PanaCast 50 VBS
        stream = self.cmd_driver.exec_pcos_cmd(f"wmic path CIM_LogicalDevice get DeviceID|findstr {self.gn_vid} | findstr 30")
        assert self.dut_audio_pid not in stream, "Check {self.dut_audio_pid} disappear fail"
        assert self.dut_video_pid not in stream, "Check {self.dut_video_pid} disappear fail"

    @pytest.mark.usefixtures("enable_teams_byod", "yield_swb_usb_connect")
    @jama_tc(Gan_TC_ESW_51374, Gan_TC_ESW_40206)
    def test_end_byod_mode_by_switch_btn(self):
        # 1 Go to Device Manager of PC, UVC and UAC devices should be listed in it.
        time.sleep(5)
        stream = self.cmd_driver.exec_pcos_cmd(f"wmic path CIM_LogicalDevice get DeviceID|findstr {self.gn_vid} | findstr 30")
        assert self.dut_audio_pid in stream, "Check {self.dut_audio_pid} appear fail"
        assert self.dut_video_pid in stream, "Check {self.dut_video_pid} appear fail"

        # 2 Click "End BYOD mode" button and Click "Confirm" button
        # A window should pop up and ask you to confirm to end BYOD or Cancel.
        self.tc_jabra_meeting_driver.byod_page().disable_byod()
        time.sleep(10)
        self.tc_teams_room_ins.check_sp_status("home_ready")

        # 3 Go to Device Manager of PC, UVC and UAC devices should be NOT listed in it.
        # UAC device: Echo Cancelling Speakerphone (Jabra PanaCast 50 VBS) (0b0e:3042)
        # UVC device: Jabra PanaCast 50 VBS
        time.sleep(3)
        stream = self.cmd_driver.exec_pcos_cmd(f"wmic path CIM_LogicalDevice get DeviceID|findstr {self.gn_vid} | findstr 30")
        assert self.dut_audio_pid not in stream, "Check {self.dut_audio_pid} disappear fail"
        assert self.dut_video_pid not in stream, "Check {self.dut_video_pid} disappear fail"
