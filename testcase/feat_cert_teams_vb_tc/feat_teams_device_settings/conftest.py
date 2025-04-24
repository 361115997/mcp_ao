import os
import random
import re
import string
import time

import pytest
from apollo_base.cmd_driver import CmdDriver
from apollo_base.nico_android_base import NicoAndroidBase
from apollo_gn_android.jose_api_driver import JoseApiDriver
from apollo_jabra.tc_jabra_meeting_driver.driver import TCJabraMeeting
from apollo_teams_room.driver import init_teams_room_driver

from testcase.base import Base


@pytest.fixture(scope="function")
def set_language_english():
    yield
    jose_api_driver = JoseApiDriver("VB")
    jose_api_driver.set_english()


@pytest.fixture(scope="function")
def pair_tc_vb():
    tc_jose_api_ins = JoseApiDriver(test_device="TC")

    # pair TC and VB from TC via JoseApiExample APP
    tc_jose_api_ins.pair_active_device(Base().tc_pair_udid)
    # Set VaaS as Teams and Launch Teams app
    tc_jose_api_ins.vaas_settings_set_provider_teams()
    tc_jose_api_ins.launch_vaas_services()


@pytest.fixture(scope="function")
def teams_start_tc_jabra_meeting_setting():
    udid = Base().tc_udid
    cmd_driver = CmdDriver(udid)
    cmd_driver.exec_adb_shell_cmd(r"settings put global policy_control immersive.navigation=*")
    rst = cmd_driver.exec_adb_shell_cmd("dumpsys window | grep mCurrentFocus")
    if "com.jabra.meeting" not in rst:
        tc_teams_room_ins = init_teams_room_driver(test_device="TC")
        tc_teams_room_ins.open()
        tc_teams_room_ins.goto_jabra_meeting()


@pytest.fixture(scope="function")
def restore_tc_default_settings():
    yield
    udid = Base().tc_udid
    cmd_driver = CmdDriver(udid)
    turn_off_high_contrast_mode = """settings put secure high_text_contrast_enabled 0"""
    cmd_driver.exec_adb_shell_cmd(turn_off_high_contrast_mode)
    set_text_size = """settings put system font_scale 1.0"""
    cmd_driver.exec_adb_shell_cmd(set_text_size)


@pytest.fixture(scope="function")
def restore_tc_network_connect():
    yield
    udid = Base().tc_udid
    cmd_driver = CmdDriver(udid)
    disable_network = "ifconfig eth0 up"
    cmd_driver.exec_adb_shell_cmd(disable_network)


@pytest.fixture(scope="function")
def restore_vb_default_settings():
    yield
    udid = Base().vb_udid
    cmd_driver = CmdDriver(udid)
    turn_off_high_contrast_mode = """settings put secure high_text_contrast_enabled 0"""
    cmd_driver.exec_adb_shell_cmd(turn_off_high_contrast_mode)
    set_text_size = """settings put system font_scale 1.0"""
    cmd_driver.exec_adb_shell_cmd(set_text_size)


@pytest.fixture(scope="function")
def reset_password():
    yield
    tc_jose_api_ins = JoseApiDriver(test_device="TC")
    tc_jose_api_ins.reset_password("123456")

@pytest.fixture(scope="function")
def get_tc_info():
    Get_teams_partner_agent_version = r"dumpsys package com.microsoft.teams.ipphone.partner.agent |grep versionName"
    Get_teams_version = r"dumpsys package com.microsoft.skype.teams.ipphone |grep versionName"
    Get_teams_authenticator_version = r"dumpsys package  com.azure.authenticator |grep versionName"
    Get_teams_admin_agent_version = r"dumpsys package com.microsoft.teams.ipphone.admin.agent |grep versionName"
    Get_teams_intune_version_a13 = r"dumpsys package  com.microsoft.intune.aospagent |grep versionName"
    tc_info_list = {}
    cmd_driver_tc = CmdDriver(Base().tc_udid)
    # get tc info
    tc_ip_address = re.findall(r"inet addr:(\d+\.\d+\.\d+\.\d+)", cmd_driver_tc.exec_adb_shell_cmd("ifconfig eth0"))[0]
    firmware_version_tc = cmd_driver_tc.exec_adb_shell_cmd("version", timeout=20).rstrip()

    # when vaas was teams, device has its special parameters
    if os.getenv("current_vaas") == "Teams":
        teams_version = cmd_driver_tc.exec_adb_shell_cmd(Get_teams_version).replace("versionName=", "").replace("\n", "").strip()
        admin_agent = cmd_driver_tc.exec_adb_shell_cmd(Get_teams_admin_agent_version, 30).replace("versionName=", "").replace("\n", "").strip()
        microsoft_intune = cmd_driver_tc.exec_adb_shell_cmd(Get_teams_intune_version_a13, 30).replace("versionName=", "").replace("\n", "").strip()
        authenticator = cmd_driver_tc.exec_adb_shell_cmd(Get_teams_authenticator_version, 30).replace("versionName=", "").replace("\n", "").strip()
        partner_agent = cmd_driver_tc.exec_adb_shell_cmd(Get_teams_partner_agent_version, 30).replace("versionName=", "").replace("\n", "").strip()
        tc_info_list["Microsoft Teams"] = teams_version
        tc_info_list["Admin Agent"] = admin_agent
        tc_info_list["Microsoft Intune"] = microsoft_intune
        tc_info_list["Authenticator"] = authenticator
        tc_info_list["Partner Agent"] = partner_agent

    # when vaas was zoom, device has its special parameters
    elif os.getenv("current_vaas") == "Zoom":
        video_app_version_tc = cmd_driver_tc.exec_adb_shell_cmd("pm dump us.zoom.zrc|grep versionName").replace("versionName=", "").replace("\n", "").strip()
        tc_info_list["Video conferencing app version"] = video_app_version_tc
    tc_info_list["Firmware version"] = firmware_version_tc
    tc_info_list["IP address"] = tc_ip_address
    tc_info_list["MAC address"] = Base().tc_mac_address
    tc_info_list["Serial number"] = Base().tc_udid
    return tc_info_list


@pytest.fixture(scope="function")
def get_vb_info():
    Get_teams_partner_agent_version = r"dumpsys package com.microsoft.teams.ipphone.partner.agent |grep versionName"
    Get_teams_version = r"dumpsys package com.microsoft.skype.teams.ipphone |grep versionName"
    Get_teams_authenticator_version = r"dumpsys package  com.azure.authenticator |grep versionName"
    Get_teams_admin_agent_version = r"dumpsys package com.microsoft.teams.ipphone.admin.agent |grep versionName"
    Get_teams_intune_version_a13 = r"dumpsys package  com.microsoft.intune.aospagent |grep versionName"

    vb_info_list = {}
    cmd_driver_vb = CmdDriver(Base().vb_udid)
    # cmd_driver_404 = CmdDriver(Base().vb404_udid)
    # use joseapi to set 'room name','description','phone','email'
    room_name = f"test{random.random()}"
    email = "".join(random.choice(string.ascii_lowercase) for i in range(6)) + "@jabra.com"
    phone = "".join(random.choice("0123456789") for i in range(11))
    description = "".join(random.choice(string.ascii_letters) for i in range(11))
    vb_joseapi_driver = JoseApiDriver("VB")
    vb_joseapi_driver.set_room_name(room_name)
    vb_joseapi_driver.set_device_support_info(description, phone, email)
    cmd_driver_vb.exec_adb_shell_cmd("am start -n com.jabra.meeting/com.jabra.meeting.MainActivity")
    time.sleep(1)
    # get vb info
    vb_ip_address = re.findall(r"inet addr:(\d+\.\d+\.\d+\.\d+)", cmd_driver_vb.exec_adb_shell_cmd("ifconfig eth0"))[0]
    firmware_version_vb = cmd_driver_vb.exec_adb_shell_cmd("info|grep 'PanaCast' | grep 'VBS -'", timeout=20).replace("\n", "")

    # audio_version = re.search(r'v(\d+\.\d+\.\d+)', cmd_driver_404.exec_adb_shell_cmd("version")).group(port_cmd 1)
    audio_version = re.search(r"V(\d+\.\d+\.\d+)", cmd_driver_vb.exec_adb_shell_cmd("newport_cmd --function=build_info", timeout=30)).group(1)
    video_version = re.search(r"(\d+\.\d+\.\d+)", cmd_driver_vb.exec_adb_shell_cmd("newport_cmd --function=mx-version", 30)).group(1)

    # when vaas was teams, device has its special parameters
    if os.getenv("current_vaas") == "Teams":
        teams_version = cmd_driver_vb.exec_adb_shell_cmd(Get_teams_version).replace("versionName=", "").replace("\n", "").strip()
        admin_agent = cmd_driver_vb.exec_adb_shell_cmd(Get_teams_admin_agent_version, 30).replace("versionName=", "").replace("\n", "").strip()
        microsoft_intune = cmd_driver_vb.exec_adb_shell_cmd(Get_teams_intune_version_a13, 30).replace("versionName=", "").replace("\n", "").strip()
        authenticator = cmd_driver_vb.exec_adb_shell_cmd(Get_teams_authenticator_version, 30).replace("versionName=", "").replace("\n", "").strip()
        partner_agent = cmd_driver_vb.exec_adb_shell_cmd(Get_teams_partner_agent_version, 30).replace("versionName=", "").replace("\n", "").strip()
        vb_info_list["Microsoft Teams"] = teams_version
        vb_info_list["Admin Agent"] = admin_agent
        vb_info_list["Microsoft Intune"] = microsoft_intune
        vb_info_list["Authenticator"] = authenticator
        vb_info_list["Partner Agent"] = partner_agent

    # when vaas was zoom, device has its special parameters
    elif os.getenv("current_vaas") == "Zoom":
        video_app_version_vb = cmd_driver_vb.exec_adb_shell_cmd("pm dump us.zoom.zrc|grep versionName").replace("versionName=", "").replace("\n", "").strip()
        vb_info_list["Video conferencing app version"] = video_app_version_vb

    vb_info_list["Audio engine version"] = audio_version
    vb_info_list["Video engine version"] = video_version
    vb_info_list["IP address"] = vb_ip_address
    vb_info_list["MAC address"] = Base().vb_mac_address
    vb_info_list["Firmware version"] = firmware_version_vb
    vb_info_list["Serial number"] = Base().vb_udid
    vb_info_list["Room name"] = room_name
    vb_info_list["Description"] = description
    vb_info_list["Phone"] = phone
    vb_info_list["Email"] = email

    return vb_info_list


@pytest.fixture(scope="function")
def resets_the_screen_timeout():
    yield
    # Unlock screen, then set device screen off timeout as 600s
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_teams_room_ins.adb_utils.unlock()
    tc_cmd_driver = CmdDriver(Base().tc_udid)
    tc_cmd_driver.exec_adb_shell_cmd("settings put system screen_off_timeout 600000")
    rst = tc_cmd_driver.exec_adb_shell_cmd("""dumpsys power | grep InteractiveModeEnabled""")
    assert "mHalInteractiveModeEnabled=true" in rst


@pytest.fixture(scope="function")
def cleanup_tc_teams_call():
    tc_teams_room_ins = init_teams_room_driver(test_device="TC")
    tc_teams_room_ins.cleanup_sp_meeting()
    tc_teams_room_ins.adb_utils.back()
    yield
    tc_teams_room_ins.cleanup_sp_meeting()
    tc_teams_room_ins.adb_utils.back()


@pytest.fixture(scope="function")
def turn_on_web_console_by_default():
    tc_jabra_meeting_driver = TCJabraMeeting()
    tc_jabra_meeting_driver.home_page().goto_admin()
    tc_jabra_meeting_driver.admin_page().goto_account_page()
    tc_jabra_meeting_driver.account_page().turn_on_web_console()
