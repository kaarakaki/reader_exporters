from nptdms import TdmsFile
import csv
import pandas as pd
import json
import os

TOTAL_SAMPLES = {'MG1': [128000],
                 'MG2': [800000, 40000],
                 'MG3': [150000]
    
}

def tdms_to_csv(working_directory, export_directory):
    """
    function to convert TDMS file to CSV
    first three characters of .tdms file should be MGX, where X is the measurement group #
    """

    for working_file in os.listdir(working_directory):
        us_2 = False
        if working_file.endswith(".tdms"):
            print("Converting file", working_file)

            in_fn = working_directory+working_file
            if working_file[0:3] == 'MG1':
                total_samples = TOTAL_SAMPLES['MG1']
            elif working_file[0:3] == 'MG2':
                total_samples = TOTAL_SAMPLES['MG2']
            elif working_file[0:3] == 'MG3':
                total_samples = TOTAL_SAMPLES['MG3']

            print("Expected samples:", total_samples)

            with TdmsFile.open(in_fn) as tdms_file:

                groups = tdms_file.groups()
                channel_ti = groups[0].channels()
                channel_log = groups[1].channels()
                time = channel_log[0].time_track()
                output_df = pd.DataFrame(time, columns=["Time"])

                #####     ITERATE OVER # CHANNELS     #####
                for i in range(0,len(channel_log)):
                    r_channel = channel_log[i]
                    # for name,value in r_channel.properties.items():
                    #     print("{0}: {1}".format(name, value))

                    
                    device_id = r_channel.properties["NI_DeviceName"]
                    channel_id = r_channel.properties["DAC~Channel~Id"]
                    module_id = r_channel.properties["DAC~Device~Name"].replace(' ','-')
                    start_time = str(r_channel.properties["wf_start_time"]).replace(':','-')

                    # print("Device ID: {0}\nChannel ID: {1}\nModule ID: {2}".format(device_id, channel_id, module_id))

                    #####     Catch different sampling rates     #####
                    if len(time) != len(channel_log[i].time_track()):
                        us_2 = True
                        manual_df = pd.DataFrame(channel_log[i].time_track(), columns=["Time"])
                        channel_name = module_id + "." + channel_id
                        data = r_channel[:]
                        ###   APPEND TO OUTPUT DF   ###
                        manual_df[channel_name] = data
                        manual_df = manual_df.truncate(before=1,after=total_samples[1])
                        break

                    channel_name = module_id + "." + channel_id
                    data = r_channel[:]

                    ###   APPEND TO OUTPUT DF   ###
                    output_df[channel_name] = data

                output_df = output_df.truncate(before=1,after=total_samples[0])

                #####     EXPORT DATA     #####
                out_fn = working_file[0:3] + "_" + str(start_time) + ".csv"
                print("Writing file ", out_fn)
                output_df.to_csv(export_directory+out_fn, sep=',', index=False, float_format='%.12f')

                #####     EXPORT SPECIAL     #####
                if us_2:
                    spec_fn = working_file[0:3] + "_" + "2_" + str(start_time) + ".csv"
                    print("Writing file ", spec_fn)
                    manual_df.to_csv(export_directory+spec_fn, sep=',', index=False, float_format='%.12f')


if __name__ == "__main__":

    with open("config.json", "r") as jfile:
        config_data = json.load(jfile)

    print(config_data)

    tdms_to_csv(config_data["input_path"],config_data["output_path"])
