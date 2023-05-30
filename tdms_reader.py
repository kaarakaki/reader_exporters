from nptdms import TdmsFile
import csv
import pandas as pd

raw_file = 'Accel_2023-05-24-07-29-15.tdms'
wd = 'C:\\Users\\KyleArakaki\\Documents\\Github\\reader_exporters\\data\\'
in_fn = wd+raw_file

with TdmsFile.open(in_fn) as tdms_file:

    groups = tdms_file.groups()
    channel_ti = groups[0].channels()
    channel_log = groups[1].channels()
    time = channel_log[0].time_track()
    output_df = pd.DataFrame(time, columns=["Time"])

    #####     ITERATE OVER # CHANNELS     #####
    for i in range(0,len(channel_log)):
        r_channel = channel_log[i]
        for name,value in r_channel.properties.items():
            print("{0}: {1}".format(name, value))
        device_id = r_channel.properties["NI_DeviceName"]
        channel_id = r_channel.properties["DAC~Channel~Id"]
        module_id = r_channel.properties["DAC~Device~Name"].replace(' ','-')
        start_time = str(r_channel.properties["wf_start_time"]).replace(':','-')

        # print("Device ID: {0}\nChannel ID: {1}\nModule ID: {2}".format(device_id, channel_id, module_id))

        channel_name = module_id + "." + channel_id
        data = r_channel[:]
        # print(type(channel_log[i][:]))
        # print(type(channel_log[i][0]))

        temp_df = pd.DataFrame(data, columns=[channel_name])

        ###   APPEND TO OUTPUT DF   ###
        output_df[channel_name] = data


    #####     EXPORT DATA     #####
    out_wd = 'C:/Users/KyleArakaki/Documents/Github/reader_exporters/export/'
    out_fn = raw_file[0:3] + "_" + str(start_time) + ".csv"

    output_df.to_csv(out_wd+out_fn, sep=',', index=False, float_format='%.12f')