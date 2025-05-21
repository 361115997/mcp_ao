import platform



def main():

    if platform.system() == "Windows":
        from apollo_makima.windows.utils.common import WinCommon

        makima_common: WinCommon = WinCommon()
        makima_common.print_windows()

    elif platform.system() == "Darwin":
        from apollo_makima.mac.utils.common import MacCommon

        makima_common: MacCommon = MacCommon()
        makima_common.print_windows()