


cookie=""

headers = {
        "Connection": "keep-alive",
        "cookie": cookie.encode("utf-8").decode("latin1")
    }

deal_file_names = []
non_metadata_file = []

SearchKEY=""

StartPage = 1
StopPage = 2
TimeSleep = 5

folder_path = ""
output_path = ""

pro_upper = 1.5
pro_lower = 0.9
pro_first_lower = 0.25