import pytest, time
from apollo_base.decorate import jama_tc
from tools.script.jama_test_case.gandalf.BYOD import *
from testcase.base import *
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_teams_room.driver import init_teams_room_driver
from apollo_teams.driver import init_apollo_teams_driver
from apollo_swb.driver import init_swb_driver
from apollo_audio.driver import AudioDriver
from apollo_pcos.driver import init_apollo_pcos_driver
from testcase.base import Base

from apollo_jabra.vb_jabra_meeting_driver.driver import VBJabraMeeting


@pytest.mark.gandalf_nightly
@pytest.mark.firefoot_nightly
@pytest.mark.feat_teams_byod_in_meeting
class TestFeatTeamsInMeeting(Base):
    def setup_class(self):
        self.audio_ins = AudioDriver()
        self.dut_name = Base().dut_name
        self.teams_ag_ins = init_apollo_teams_driver(script_exe_env="PC_AG_WIN")
        self.teams_ep_ins = init_apollo_teams_driver(script_exe_env="PC_EP_WIN")
        self.teams_ag_user = Base().pc_ag_win["Teams"]["user"]
        self.teams_ep_user = Base().pc_ep_win["Teams"]["user"]
        self.tc_jabra_meeting_driver = TCJabraMeeting()
        self.pcos_ins = init_apollo_pcos_driver()
        self.vb_jabra_meeting_driver = VBJabraMeeting()
        self.swb_usb = init_swb_driver(Base().swb_ctrl_unit)
        self.swb_hdmi = init_swb_driver("arduino")
        os.environ["current_vaas"] = "Teams"

    def teardown_class(self):
        self.teams_ep_ins.cleanup_sp_meeting()
        self.teams_ag_ins.cleanup_sp_meeting()
        # # Disconnect after the test execute done, because HDMI in will auto share cause other test case fail
        self.swb_hdmi.disconn_hdmi_from_monitor_hub()

    @pytest.mark.usefixtures("create_or_start_teams_byod_meeting")
    @jama_tc(Gan_TC_ESW_51377, Gan_TC_ESW_40211)
    def test_audio_controls_in_meeting(self):

        # 1 Check Audio
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")

        # 2 Click "Mute"/"Unmute" button on TC
        self.tc_jabra_meeting_driver.byod_page().mute_meeting()
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_no_tx(self.dut_name, "PC_EP_WIN")

        self.tc_jabra_meeting_driver.byod_page().unmute_meeting()
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")

        # 3 Increase/decrease the volume from TC
        self.tc_jabra_meeting_driver.byod_page().switch_spk_vol("lowest")
        time.sleep(2)
        volume_value = self.pcos_ins.get_speaker_volume()
        assert int(volume_value) == 0
        time.sleep(3)

        self.tc_jabra_meeting_driver.byod_page().switch_spk_vol("highest")
        time.sleep(2)
        volume_value = self.pcos_ins.get_speaker_volume()
        assert int(volume_value) == 100

    @pytest.mark.usefixtures("create_or_start_teams_byod_meeting")
    @jama_tc(Gan_TC_ESW_51378, Gan_TC_ESW_40212)
    def test_camera_controls_in_meeting(self):
        # 1 Check is working
        self.teams_ep_ins.check_dut_camera_video_valid(self.teams_ag_user, False, False)

        # 2 Perform the PTZ in random

        # Should add check PTZ value in the furture both video compare and jose_control_service read value
        self.tc_jabra_meeting_driver.byod_page().goto_panoramic_view_mode()
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_zoom_in", 20)
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_tilt_up", 10)
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_tilt_down", 10)
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_pan_left", 10)
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_pan_right", 10)
        self.tc_jabra_meeting_driver.byod_page().modify_settings("camera_zoom_out", 20)

        # 3 Check the Video still work
        self.teams_ep_ins.check_dut_camera_video_valid(self.teams_ag_user, False, False)

    @pytest.mark.usefixtures("create_or_start_teams_byod_meeting", "yield_swb_usb_connect")
    @jama_tc(Gan_TC_ESW_51383)
    def test_connect_hdmi_in_share_content_locally_in_meeting(self):
        # 1 Disconnect HDMI cable from the PC
        # VB should show "To view your screen on the meeting room monitor, connect a HDMI cable between the video bar and your computer".
        self.swb_hdmi.disconn_hdmi_from_monitor_hub()

        time.sleep(5)
        self.vb_jabra_meeting_driver.byod_page().check_display_as_hdmi_in_disconnect()

        # 2 Connect HDMI cable to the PC again
        # DUT should show the content what PC is sharing again.
        self.swb_hdmi.conn_hdmi_to_monitor_hub()
        time.sleep(5)
        self.vb_jabra_meeting_driver.byod_page().check_display_as_sharing()

        # 3 Check the the audio and video in the meeting
        self.audio_ins.verify_call_rx(self.dut_name, "PC_EP_WIN")
        self.audio_ins.verify_call_tx(self.dut_name, "PC_EP_WIN")
        self.teams_ep_ins.check_dut_camera_video_valid(self.teams_ag_user, False, False)

    @pytest.mark.usefixtures("create_or_start_teams_byod_meeting", "yield_swb_usb_connect")
    @jama_tc(Gan_TC_ESW_51384, Gan_TC_ESW_45300)
    def test_connect_usb_then_hdmi_in_vaas_mode(self):
        # 1 Connect DUT to a PC via USB-C, then connect HDMI to PC
        self.swb_hdmi.conn_hdmi_to_monitor_hub()
        time.sleep(5)
        # 2 Disconnect HDMI cable from the PC
        # VB should show "To view your screen on the meeting room monitor, connect a HDMI cable between the video bar and your computer".
        self.swb_hdmi.disconn_hdmi_from_monitor_hub()
        time.sleep(5)
        self.vb_jabra_meeting_driver.byod_page().check_display_as_hdmi_in_disconnect()

        # 3 Connect HDMI cable to the PC again
        # VB should show the content what PC is sharing again.
        self.swb_hdmi.conn_hdmi_to_monitor_hub()
        time.sleep(10)
        self.vb_jabra_meeting_driver.byod_page().check_display_as_sharing()

        #### The Step 4 and 5 can not be tested now because we use USB to control VB, once disconnect will lost control, align with Sunny we can comment out for a moment, suggest us can use wireless adb to control instead in furture.
        # 4 Disconnect USB-C cable from the PC
        # VB should still show the content what PC is sharing after switch to Teams Room. TC returns to VaaS's UI.
        # self.swb_usb.disconn_dut_from_apollo(self.dut_name)
        # self.vb_jabra_meeting_driver.byod_page().check_display_as_sharing()

        # 5 Disconnect HDMI cable from the PC,  VB should return to VaaS's UI.
        # self.swb_hdmi.disconn_hdmi_from_monitor_hub()
