import glob
import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
import pathlib, glob, time, subprocess

def read(path, json_file):
    """
    :param path: str
    :param json_file: str
    :return DataFrame
    """
    return pd.read_json(path + json_file)

def to_files(data_frame: pd.DataFrame, out_path):
    os.makedirs(out_path,exist_ok=True)

    for idx, row in data_frame.iterrows():
        file_name = f"{idx}.c"
        with open(out_path + file_name, 'w') as f:
            f.write(row.func)

def slice_frame(data_frame: pd.DataFrame, size: int):
    data_frame_size = len(data_frame)
    return data_frame.groupby(np.arange(data_frame_size) // size)

def main(jsonPath,jsonFile,parsePath,outputPath,repr = "cfg",format = "dot",splitJsonFunc=True):
    """
    :required param jsonPath: str #"./dataset/raw/"
    :required param jsonFile: str #"test1.json"
    :required param parsePath: str #./dataset/samplesTest/
    :required outputPath: str #./dataset/cfgsTest/
    """

    if splitJsonFunc:
        rawDataFrame = read(jsonPath, jsonFile)
        #separate samples on .c files 
        to_files(rawDataFrame,parsePath)


    #get all .c files we just generated
    project = glob.glob(parsePath+'/*')   
    num = 0 
    #create cfg files for each sample file
    try:
                folderNum = str(num)
                # get the start time
                st = time.time()
                s = subprocess.getstatusoutput("joern-parse " + parsePath+ "")
                if s[0] == 0:
                    print(s[1])
                else:
                    print('Error: {}'.format(s[1]))     
                s2 = subprocess.getstatusoutput("joern-export --repr="+ repr +" --format=" +format+" --out " + outputPath)
                if s2[0] == 0:
                    print(s2[1])
                    num = num + 1
                else:
                    print('Error: {}'.format(s2[1]))  
                    num = num + 1
                print('Execution time:', time.time()-st, 'seconds')
    except:
                 print('Error: {}'.format(s[1]))  
                 print('Error: {}'.format(s2[1]))  
    
   # try:  
      #s3 = subprocess.getstatusoutput("find /home/ubuntu/cpgCode/dataset/cpg/ -type f ! -name '1-cfg*' -delete")
    #except:
     # print('Error: {}'.format(s3[1]))
                     

if __name__ == "__main__":

    jsonPath= "./dataset/json/"
    jsonFile= "train.json"
    parsePath= "./dataset/files/"
    outputPath= "./dataset/cfg/"
    repr = "cfg"
    format = "dot"
    splitJsonFunc = False #set to true only if you want to create .c files 

    main(jsonPath,jsonFile,parsePath,outputPath,repr,format,splitJsonFunc)

